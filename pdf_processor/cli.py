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

@click.group()
def cli():
    """Finance Dashboard PDF Processor CLI."""
    load_dotenv()

@cli.command()
@click.option("--dry-run", is_flag=True, help="Run without moving files.")
def process(dry_run):
    """Process all pending PDFs."""
    
    # Load config from env
    pdf_dir = Path(os.getenv("PDF_INPUT_DIR", "data/pdfs"))
    csv_dir = Path(os.getenv("CSV_OUTPUT_DIR", "data/csv"))
    processed_dir = Path(os.getenv("PROCESSED_DIR", "data/processed"))
    failed_dir = Path(os.getenv("FAILED_DIR", "data/failed"))
    timeout = int(os.getenv("PDF_TIMEOUT_SECONDS", "30"))
    
    logger.info("Starting PDF processing", dry_run=dry_run)
    
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
