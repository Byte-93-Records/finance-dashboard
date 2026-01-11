import os
import click
import structlog
import logging
from pathlib import Path
from dotenv import load_dotenv

from .file_handler import FileHandler
from .router import PDFRouter
from .validator import CSVValidator
from .exceptions import PDFProcessorError

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()


def is_running_in_docker() -> bool:
    """Detect if we're running inside a Docker container."""
    # Check for .dockerenv file (most reliable)
    if Path("/.dockerenv").exists():
        return True
    # Check if /data directory exists and is writable (Docker mount)
    data_path = Path("/data")
    if data_path.exists():
        try:
            # Try to check if writable
            return os.access(data_path, os.W_OK)
        except:
            pass
    return False


def get_default_paths() -> dict:
    """Get default paths based on environment (Docker vs local)."""
    if is_running_in_docker():
        return {
            "pdf_dir": "/data/pdfs",
            "csv_dir": "/data/csv",
            "processed_dir": "/data/processed",
            "failed_dir": "/data/failed",
        }
    else:
        return {
            "pdf_dir": "data/pdfs",
            "csv_dir": "data/csvs",
            "processed_dir": "data/processed",
            "failed_dir": "data/failed",
        }


@click.group()
def cli():
    """Finance Dashboard PDF Processor CLI."""
    load_dotenv()

@cli.command()
@click.option("--dry-run", is_flag=True, help="Run without moving files.")
def process(dry_run):
    """Process all pending PDFs."""

    # Get defaults based on environment
    in_docker = is_running_in_docker()
    defaults = get_default_paths()

    # Load config from env, falling back to environment-appropriate defaults
    # Note: If env vars are set to Docker paths but we're not in Docker, use local defaults
    pdf_dir_env = os.getenv("PDF_INPUT_DIR")
    csv_dir_env = os.getenv("CSV_OUTPUT_DIR")
    processed_dir_env = os.getenv("PROCESSED_DIR")
    failed_dir_env = os.getenv("FAILED_DIR")

    # If env vars point to /data/* but we're not in Docker, ignore them
    def resolve_path(env_val, default):
        if env_val and env_val.startswith("/data") and not in_docker:
            return default
        return env_val if env_val else default

    pdf_dir = Path(resolve_path(pdf_dir_env, defaults["pdf_dir"]))
    csv_dir = Path(resolve_path(csv_dir_env, defaults["csv_dir"]))
    processed_dir = Path(resolve_path(processed_dir_env, defaults["processed_dir"]))
    failed_dir = Path(resolve_path(failed_dir_env, defaults["failed_dir"]))
    timeout = int(os.getenv("PDF_TIMEOUT_SECONDS", "30"))

    # Create directories if they don't exist
    for dir_path in [csv_dir, processed_dir, failed_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Starting PDF processing",
        dry_run=dry_run,
        environment="docker" if in_docker else "local",
        pdf_dir=str(pdf_dir),
        csv_dir=str(csv_dir),
    )
    
    try:
        file_handler = FileHandler(pdf_dir, processed_dir, failed_dir)
        router = PDFRouter(timeout_seconds=timeout)
        validator = CSVValidator()
        
        pdfs = file_handler.list_pending_pdfs()
        logger.info(f"Found {len(pdfs)} pending PDFs")
        
        processed_count = 0
        failed_count = 0
        
        for pdf_path in pdfs:
            log = logger.bind(pdf_file=pdf_path.name)
            log.info("Processing file")
            
            try:
                # Extract
                if not dry_run:
                    csv_path = router.extract(pdf_path, csv_dir)
                    log.info("Extraction successful", csv_file=csv_path.name)
                    
                    # Validate
                    try:
                        validator.validate(csv_path)
                        log.info("Validation successful")
                    except Exception as e:
                        log.warning("Validation failed, but keeping CSV for manual inspection", error=str(e))
                        
                    # Move to processed
                    file_handler.move_to_processed(pdf_path)
                    processed_count += 1
                else:
                    log.info("Dry run: Skipping extraction and move")
                    processed_count += 1 # Count as processed for dry run summary? Or maybe separate?
                    
            except PDFProcessorError as e:
                log.error("Processing failed", error=str(e))
                failed_count += 1
                if not dry_run:
                    file_handler.move_to_failed(pdf_path, str(e))
            except Exception as e:
                log.error("Unexpected error", error=str(e))
                failed_count += 1
                if not dry_run:
                    file_handler.move_to_failed(pdf_path, f"Unexpected error: {e}")
                    
        logger.info("Processing complete", processed=processed_count, failed=failed_count)
        
    except Exception as e:
        logger.critical("Critical error", error=str(e))
        raise click.Abort()

if __name__ == "__main__":
    cli()
