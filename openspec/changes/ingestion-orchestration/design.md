# Design: Ingestion Orchestration

## Context

The ETL pipeline components exist independently (PDF extraction, CSV parsing, database loading). This design addresses **orchestration** to coordinate these components into a cohesive end-to-end workflow.

**Current State:**
- PDF processor extracts PDFs to CSVs
- CSV parser validates CSV data
- Database repositories load transactions
- Components work independently but need coordination

**Constraints:**
- **Atomic Operations**: Each PDF processed atomically (all-or-nothing)
- **Error Isolation**: One failed PDF doesn't stop processing of others
- **Idempotent**: Re-running import on same PDFs safe (deduplication handles it)
- **User-Friendly**: Clear CLI with progress indicators and error messages
- **Batch Processing**: Process multiple PDFs in one command

## Goals / Non-Goals

**Goals:**
1. Coordinate Extract → Transform → Load phases for each PDF
2. Provide CLI for manual import triggering
3. Handle errors gracefully with detailed logging
4. Generate summary reports (processed, failed, imported counts)
5. Support dry-run mode for testing
6. Enable account creation via CLI

**Non-Goals:**
- Real-time processing (batch mode sufficient)
- Web UI (CLI only for v1)
- Automated scheduling (manual trigger for v1, scheduler in v2)
- Email notifications (logs sufficient for v1)
- Parallel processing (sequential processing simpler, sufficient for personal use)

## Decisions

### Decision 1: Orchestrator Coordinates All Three Phases
**Choice:** Single `IngestionOrchestrator` class coordinates PDF → CSV → Database

**Flow:**
```python
for pdf_path in pending_pdfs:
    try:
        # Extract phase
        csv_path = pdf_extractor.extract(pdf_path)
        
        # Transform phase
        transactions = csv_parser.parse(csv_path)
        
        # Load phase
        result = transaction_repo.bulk_create(transactions)
        
        # Success: move files, log result
        file_handler.move_to_processed(pdf_path)
        import_log_repo.create(success_log)
    except Exception as e:
        # Failure: move to failed, log error
        file_handler.move_to_failed(pdf_path, error=e)
        import_log_repo.create(failure_log)
```

**Rationale:**
- **Single Responsibility**: Orchestrator only coordinates, doesn't implement ETL logic
- **Error Handling**: Try-catch per PDF isolates failures
- **Logging**: Import logs track success/failure per PDF

### Decision 2: Click for CLI Framework
**Choice:** Use Click library for command-line interface

**Commands:**
```bash
finance-import process --account-id=1              # Process all PDFs for account
finance-import process --account-id=1 --dry-run    # Simulate without changes
finance-import status                              # Show import statistics
finance-import create-account --name="Chase Checking" --type="checking"
```

**Rationale:**
- **User-Friendly**: Click provides help text, argument validation, colored output
- **Pythonic**: Decorator-based API, integrates well with Python codebase
- **Standard**: Industry-standard CLI framework (used by Flask, etc.)

### Decision 3: Sequential Processing (No Parallelization)
**Choice:** Process PDFs one at a time, not in parallel

**Rationale:**
- **Simplicity**: No concurrency bugs, easier to debug
- **Resource Control**: Docling PDF extraction memory-intensive
- **Personal Use Scale**: 10-20 PDFs/month doesn't need parallelization
- **Database Safety**: No concurrent transaction conflicts

### Decision 4: Dry-Run Mode for Testing
**Choice:** `--dry-run` flag simulates import without database writes or file moves

**Behavior:**
- Extract PDFs to temporary directory (not `/data/csv/`)
- Parse CSVs and validate
- Log what would be imported (transaction count, duplicates)
- Don't write to database
- Don't move files
- Print summary of what would happen

**Rationale:**
- **Testing**: Users can verify PDFs parse correctly before committing
- **Debugging**: Identify issues without corrupting data
- **Confidence**: See results before making changes

## Implementation Architecture

### Module Structure
```
ingestion/
├── __init__.py
├── orchestrator.py     # IngestionOrchestrator class
├── cli.py             # Click CLI commands
├── hasher.py          # Transaction hash generation (already created)
└── exceptions.py      # IngestionError

# CLI entry point in pyproject.toml:
[project.scripts]
finance-import = "ingestion.cli:main"
```

### Core Classes

**IngestionOrchestrator:**
```python
class IngestionOrchestrator:
    def __init__(self, pdf_extractor, csv_parser, transaction_repo, import_log_repo, file_handler):
        # Dependency injection (TransactionHasher imported from csv_parser.hasher)
        
    def process_pending_pdfs(self, account_id: int, dry_run: bool = False) -> IngestionSummary:
        # Scan /data/pdfs/, process each PDF through ETL pipeline
        
    def process_single_pdf(self, pdf_path: Path, account_id: int, dry_run: bool = False) -> IngestionResult:
        # Process one PDF: extract → parse → load
```

**IngestionSummary:**
```python
@dataclass
class IngestionSummary:
    pdfs_processed: int
    pdfs_failed: int
    transactions_imported: int
    transactions_skipped: int  # Duplicates
    errors: list[str]
```

### CLI Commands

**Process Command:**
```bash
finance-import process --account-id=1 [--dry-run] [--verbose]
```

**Status Command:**
```bash
finance-import status
# Output:
# Total Accounts: 3
# Total Transactions: 1,234
# Last Import: 2024-01-15 10:30:00
# Pending PDFs: 5
```

**Create Account Command:**
```bash
finance-import create-account --name="Chase Checking" --type="checking" --institution="Chase Bank"
```

## Risks / Trade-offs

### Risk 1: Long-Running Imports
**Risk:** Processing 20 PDFs may take 5+ minutes (user impatience)

**Mitigation:**
- Progress bar showing "Processing 3/20 PDFs..."
- Verbose mode shows per-PDF status
- Dry-run mode for quick validation

**Likelihood:** Low (personal use rarely has 20+ PDFs at once)  
**Impact:** Low (user can walk away, check logs later)

### Risk 2: Partial Failures
**Risk:** 10 PDFs succeed, 5 fail - user may not notice failures

**Mitigation:**
- Summary report highlights failures: "15 processed, 5 failed (see /data/failed/)"
- Failed PDFs moved to `/data/failed/` with error logs
- Exit code non-zero if any failures (for scripting)

### Trade-off 1: No Automated Scheduling (v1)
**Accepted:** Users must manually run `finance-import process`

**Justification:**
- Simpler implementation (no APScheduler, no daemon process)
- Manual control acceptable for personal finance (monthly statements)
- Can add cron job if desired: `0 2 * * * finance-import process --account-id=1`
- Automated scheduling in v2 if user demand

### Trade-off 2: Sequential Processing
**Accepted:** PDFs processed one at a time (not parallel)

**Justification:**
- Personal use scale doesn't need parallelization (10-20 PDFs/month)
- Simpler code, easier debugging
- Avoids Docling memory issues with concurrent extraction
- Can add parallelization in v2 if needed

## Migration Plan

**Initial Setup:**
1. Create `ingestion/` module
2. Add Click dependency to `pyproject.toml`
3. Configure CLI entry point in `pyproject.toml`
4. Install: `uv pip install -e .` (editable install for CLI)

**Testing Approach:**
1. Integration tests: End-to-end PDF → database with sample PDFs
2. CLI tests: Invoke commands programmatically, verify output
3. Dry-run tests: Verify no database writes or file moves
4. Error handling tests: Malformed PDFs, validation failures, database errors

**Rollback Plan:**
- Remove `ingestion/` module
- Remove Click dependency from `pyproject.toml`
- Remove CLI entry point
- Components (PDF processor, CSV parser, database) still work independently

## Open Questions

1. **Progress Indicators**: Should we show per-transaction progress or just per-PDF?
   - **Recommendation**: Per-PDF only (simpler, sufficient)

2. **Account ID Requirement**: Should account ID be required or auto-detected from CSV metadata?
   - **Recommendation**: Required for v1 (explicit, prevents errors), auto-detect in v2

3. **Logging Verbosity**: Should default be verbose or quiet?
   - **Recommendation**: Quiet by default, `--verbose` flag for detailed logs

4. **Failed PDF Retry**: Should CLI have command to retry failed PDFs?
   - **Recommendation**: Yes, add `finance-import retry` command in v2
