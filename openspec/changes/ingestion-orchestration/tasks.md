# Tasks: Ingestion Orchestration

## 1. Project Setup
- [ ] 1.1 Verify `ingestion/` module exists (created in csv-parser-and-database change)
- [ ] 1.2 Add Click dependency to `pyproject.toml` (>= 8.1)
- [ ] 1.3 Configure CLI entry point in `pyproject.toml`:
  ```
  [project.scripts]
  finance-import = "ingestion.cli:main"
  ```
- [ ] 1.4 Install in editable mode: `uv pip install -e .`
- [ ] 1.5 Verify CLI works: `finance-import --help`

## 2. Orchestrator Implementation
- [ ] 2.1 Implement `IngestionOrchestrator` class in `ingestion/orchestrator.py`:
  - [ ] 2.1.1 `__init__` with dependency injection (pdf_extractor, csv_parser, repos, file_handler)
  - [ ] 2.1.2 `process_pending_pdfs(account_id, dry_run) -> IngestionSummary`
  - [ ] 2.1.3 `process_single_pdf(pdf_path, account_id, dry_run) -> IngestionResult`
- [ ] 2.2 Create `IngestionSummary` dataclass (pdfs_processed, pdfs_failed, transactions_imported, transactions_skipped, errors)
- [ ] 2.3 Create `IngestionResult` dataclass (success, transactions_imported, transactions_skipped, error_message)
- [ ] 2.4 Implement ETL coordination logic:
  - [ ] 2.4.1 Extract phase: Call `pdf_extractor.extract(pdf_path)`
  - [ ] 2.4.2 Transform phase: Call `csv_parser.parse(csv_path)`
  - [ ] 2.4.3 Load phase: Call `transaction_repo.bulk_create(transactions)`
  - [ ] 2.4.4 Success: Move PDF to `/data/processed/`, create import log
  - [ ] 2.4.5 Failure: Move PDF to `/data/failed/`, create error log
- [ ] 2.5 Add error handling (try-catch per PDF, continue on failure)
- [ ] 2.6 Add dry-run mode (skip database writes and file moves)

## 3. CLI Implementation - Process Command
- [ ] 3.1 Create `ingestion/cli.py` with Click commands
- [ ] 3.2 Implement `process` command:
  - [ ] 3.2.1 `@click.command()` decorator
  - [ ] 3.2.2 `--account-id` option (required, type=int)
  - [ ] 3.2.3 `--dry-run` flag (default=False)
  - [ ] 3.2.4 `--verbose` flag (default=False)
- [ ] 3.3 Add progress indicator (e.g., "Processing 3/10 PDFs...")
- [ ] 3.4 Add colored output (green for success, red for errors)
- [ ] 3.5 Print summary report:
  ```
  ✓ Processed: 8 PDFs
  ✗ Failed: 2 PDFs (see /data/failed/)
  → Imported: 234 transactions
  → Skipped: 12 duplicates
  ```
- [ ] 3.6 Set exit code: 0 if all success, 1 if any failures

## 4. CLI Implementation - Status Command
- [ ] 4.1 Implement `status` command:
  - [ ] 4.1.1 Query total accounts from database
  - [ ] 4.1.2 Query total transactions from database
  - [ ] 4.1.3 Query last import date from import_logs
  - [ ] 4.1.4 Count pending PDFs in `/data/pdfs/`
- [ ] 4.2 Print formatted status:
  ```
  Finance Dashboard Status
  ========================
  Accounts: 3
  Transactions: 1,234
  Last Import: 2024-01-15 10:30:00
  Pending PDFs: 5
  ```

## 5. CLI Implementation - Create Account Command
- [ ] 5.1 Implement `create-account` command:
  - [ ] 5.1.1 `--name` option (required)
  - [ ] 5.1.2 `--type` option (required, choices: checking, savings, credit_card, brokerage)
  - [ ] 5.1.3 `--institution` option (optional)
- [ ] 5.2 Validate account name uniqueness
- [ ] 5.3 Create account via `AccountRepository.create()`
- [ ] 5.4 Print success message with account ID

## 6. Dependency Injection Setup
- [ ] 6.1 Create factory function to instantiate orchestrator with all dependencies
- [ ] 6.2 Initialize PDFExtractor
- [ ] 6.3 Initialize CSVParser
- [ ] 6.4 Initialize repositories (TransactionRepository, ImportLogRepository, AccountRepository)
- [ ] 6.5 Initialize FileHandler
- [ ] 6.6 Initialize IngestionOrchestrator with all dependencies

## 7. Error Handling
- [ ] 7.1 Handle PDF extraction failures (Docling errors, timeout)
- [ ] 7.2 Handle CSV parsing failures (validation errors)
- [ ] 7.3 Handle database failures (connection errors, constraint violations)
- [ ] 7.4 Handle file system errors (permission denied, disk full)
- [ ] 7.5 Log all errors with structured logging (JSON format)
- [ ] 7.6 Create error log files in `/data/failed/` with stack traces

## 8. Testing - Unit Tests
- [ ] 8.1 Test `IngestionOrchestrator.process_single_pdf()`:
  - [ ] 8.1.1 Success case (PDF → CSV → database)
  - [ ] 8.1.2 Extraction failure (Docling error)
  - [ ] 8.1.3 Parsing failure (validation error)
  - [ ] 8.1.4 Database failure (constraint violation)
  - [ ] 8.1.5 Dry-run mode (no database writes)
- [ ] 8.2 Test `IngestionOrchestrator.process_pending_pdfs()`:
  - [ ] 8.2.1 Multiple PDFs (some succeed, some fail)
  - [ ] 8.2.2 Empty directory (no PDFs)
  - [ ] 8.2.3 Summary report accuracy

## 9. Testing - Integration Tests
- [ ] 9.1 End-to-end test: PDF → CSV → database
  - [ ] 9.1.1 Place sample PDF in `/data/pdfs/`
  - [ ] 9.1.2 Run `finance-import process --account-id=1`
  - [ ] 9.1.3 Verify transactions in database
  - [ ] 9.1.4 Verify PDF moved to `/data/processed/`
  - [ ] 9.1.5 Verify import log created
- [ ] 9.2 Test dry-run mode:
  - [ ] 9.2.1 Run `finance-import process --account-id=1 --dry-run`
  - [ ] 9.2.2 Verify no database writes
  - [ ] 9.2.3 Verify no file moves
  - [ ] 9.2.4 Verify summary report shows what would happen
- [ ] 9.3 Test failure handling:
  - [ ] 9.3.1 Place malformed PDF in `/data/pdfs/`
  - [ ] 9.3.2 Run import
  - [ ] 9.3.3 Verify PDF moved to `/data/failed/`
  - [ ] 9.3.4 Verify error log created
  - [ ] 9.3.5 Verify exit code is 1

## 10. Testing - CLI Tests
- [ ] 10.1 Test `finance-import --help` (shows usage)
- [ ] 10.2 Test `finance-import process --help` (shows process options)
- [ ] 10.3 Test `finance-import status` (shows statistics)
- [ ] 10.4 Test `finance-import create-account` (creates account)
- [ ] 10.5 Test invalid arguments (missing --account-id, invalid --type)

## 11. Documentation
- [ ] 11.1 Add CLI usage to `README.md`:
  - [ ] 11.1.1 Installation instructions
  - [ ] 11.1.2 Creating accounts
  - [ ] 11.1.3 Processing PDFs
  - [ ] 11.1.4 Checking status
  - [ ] 11.1.5 Dry-run mode
- [ ] 11.2 Document error handling and troubleshooting
- [ ] 11.3 Add examples with screenshots/output

## 12. Code Quality
- [ ] 12.1 Add type hints to all functions
- [ ] 12.2 Add docstrings (Google style)
- [ ] 12.3 Run Black formatter
- [ ] 12.4 Run isort
- [ ] 12.5 Run flake8
- [ ] 12.6 Verify mypy compliance

## 13. Validation & Deployment
- [ ] 13.1 Run full test suite (all tests pass)
- [ ] 13.2 Test with real financial PDFs (3+ banks)
- [ ] 13.3 Verify CLI works in Docker container
- [ ] 13.4 Verify error messages are clear and actionable
- [ ] 13.5 Create PR for review
- [ ] 13.6 Update `CHANGELOG.md`
