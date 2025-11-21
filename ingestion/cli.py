import click
from pathlib import Path
from database.connection import get_db
from database.repositories import TransactionRepository, AccountRepository, ImportLogRepository
from csv_parser.parser import CSVParser
from .orchestrator import IngestionOrchestrator

@click.group()
def main():
    """Finance Dashboard Ingestion CLI"""
    pass

@main.command()
@click.option("--account-id", required=True, type=int, help="Account ID to import into")
@click.option("--dry-run", is_flag=True, help="Run without saving changes")
@click.option("--file", type=click.Path(exists=True), help="Specific file to process")
def process(account_id, dry_run, file):
    """Process pending PDFs or a specific file"""
    db = next(get_db())
    repo = TransactionRepository(db)
    # ... other repos
    
    orchestrator = IngestionOrchestrator(None, CSVParser(), repo, None, None)
    
    if file:
        path = Path(file)
        if path.suffix.lower() == ".csv":
            summary = orchestrator.process_csv(path, account_id, dry_run)
            click.echo(f"Processed CSV: {summary}")
        else:
            click.echo("Only CSV supported in this stub for now")
    else:
        click.echo("Processing pending files...")

if __name__ == "__main__":
    main()
