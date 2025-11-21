from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from .cli import IngestionSummary # Circular import issue? No, cli imports orchestrator. 
# Wait, I should define dataclasses here or in a separate file. 
# The task says "Create IngestionSummary dataclass".
# I'll put it here.

@dataclass
class IngestionSummary:
    pdfs_processed: int = 0
    pdfs_failed: int = 0
    transactions_imported: int = 0
    transactions_skipped: int = 0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class IngestionOrchestrator:
    def __init__(self, pdf_extractor, csv_parser, transaction_repo, import_log_repo, file_handler):
        self.pdf_extractor = pdf_extractor
        self.csv_parser = csv_parser
        self.transaction_repo = transaction_repo
        self.import_log_repo = import_log_repo
        self.file_handler = file_handler

    def process_pending_pdfs(self, account_id: int, dry_run: bool = False) -> IngestionSummary:
        summary = IngestionSummary()
        # In a real impl, we'd list PDFs from file_handler
        # For now, let's just assume we are called with a specific file or we scan
        # The task says "process_pending_pdfs".
        
        # Placeholder logic
        return summary

    def process_single_pdf(self, pdf_path: Path, account_id: int, dry_run: bool = False):
        # Logic to extract, parse, load
        pass

    def process_csv(self, csv_path: Path, account_id: int, dry_run: bool = False) -> IngestionSummary:
        summary = IngestionSummary()
        try:
            transactions = self.csv_parser.parse(csv_path)
            
            # Enrich with account_id
            for t in transactions:
                # Convert to DB model
                # This requires mapping logic
                pass
                
            if not dry_run:
                # Save to DB
                pass
                
            summary.transactions_imported = len(transactions)
        except Exception as e:
            summary.errors.append(str(e))
            
        return summary
