# Tasks: PDF to CSV Extraction

## 1. Project Setup
- [ ] 1.1 Create `/data/` directory structure (`pdfs/`, `csv/`, `processed/`, `failed/`)
- [ ] 1.2 Add Docling to `pyproject.toml` with version constraint
- [ ] 1.3 Update `.env.example` with PDF processor configuration variables
- [ ] 1.4 Add volume mounts for `/data/` in `docker-compose.yml`
- [ ] 1.5 Configure Docker service for PDF processor with appropriate memory limits

## 2. Core Module Implementation
- [ ] 2.1 Create `pdf_processor/` module structure with `__init__.py`
- [ ] 2.2 Implement `models.py` with Pydantic models for CSV schema (TransactionRow, CSVOutput)
- [ ] 2.3 Implement `exceptions.py` with custom exceptions (ExtractionError, ValidationError, FileHandlerError)
- [ ] 2.4 Implement `file_handler.py` with FileHandler class:
  - [ ] 2.4.1 `list_pending_pdfs()` - scan `/data/pdfs/` directory
  - [ ] 2.4.2 `move_to_processed()` - atomic move to `/data/processed/`
  - [ ] 2.4.3 `move_to_failed()` - move to `/data/failed/` with error log
  - [ ] 2.4.4 Ensure read-only PDF handling (never modify originals)

## 3. PDF Extraction
- [ ] 3.1 Implement `extractor.py` with PDFExtractor class
- [ ] 3.2 Integrate Docling library for PDF-to-CSV conversion
- [ ] 3.3 Configure Docling for financial statement table extraction
- [ ] 3.4 Implement `extract(pdf_path: Path) -> Path` method
- [ ] 3.5 Add timeout handling (30 seconds per PDF)
- [ ] 3.6 Add memory limit error handling
- [ ] 3.7 Write extraction errors to structured logs

## 4. CSV Validation
- [ ] 4.1 Implement `validator.py` with CSVValidator class
- [ ] 4.2 Implement schema validation (required columns: transaction_date, description, amount, transaction_type)
- [ ] 4.3 Add date format validation (YYYY-MM-DD)
- [ ] 4.4 Add amount precision validation (Decimal type, 2 decimal places)
- [ ] 4.5 Implement `validate(csv_path: Path) -> ValidationResult` method
- [ ] 4.6 Generate detailed validation error messages

## 5. Orchestration
- [ ] 5.1 Create main processing script (`pdf_processor/cli.py`)
- [ ] 5.2 Implement batch processing loop (scan → extract → validate → move)
- [ ] 5.3 Add command-line interface with Click library
- [ ] 5.4 Implement logging with structlog (JSON structured logs)
- [ ] 5.5 Add dry-run mode for testing without file moves
- [ ] 5.6 Add summary reporting (processed count, failed count, errors)

## 6. Testing
- [ ] 6.1 Create `tests/pdf_processor/` directory structure
- [ ] 6.2 Collect 9-15 anonymized financial statement PDFs:
  - [ ] 6.2.1 Bank statements (Chase, BoA, Wells Fargo, Citi, etc.)
  - [ ] 6.2.2 Credit card statements (Amex, Visa/MC, Discover, Capital One)
  - [ ] 6.2.3 Brokerage statements (Fidelity, Schwab, TD Ameritrade, E*TRADE)
- [ ] 6.3 Write unit tests for CSVValidator (valid/invalid schemas)
- [ ] 6.4 Write unit tests for FileHandler (file operations, error cases)
- [ ] 6.5 Write integration tests for PDFExtractor with fixture PDFs
- [ ] 6.6 Write end-to-end tests (PDF → CSV → validation → file moves)
- [ ] 6.7 Add test for large PDF handling (>10MB)
- [ ] 6.8 Add test for malformed PDF handling
- [ ] 6.9 Verify 80% test coverage requirement
- [ ] 6.10 Add pytest fixtures for test PDFs and directory structures

## 7. Configuration & Documentation
- [ ] 7.1 Add environment variables to `.env`:
  - [ ] `PDF_INPUT_DIR=/data/pdfs`
  - [ ] `CSV_OUTPUT_DIR=/data/csv`
  - [ ] `PROCESSED_DIR=/data/processed`
  - [ ] `FAILED_DIR=/data/failed`
  - [ ] `PDF_TIMEOUT_SECONDS=30`
- [ ] 7.2 Document CSV schema in `docs/csv_schema.md`
- [ ] 7.3 Document PDF requirements (text-based, max 50MB) in `docs/pdf_requirements.md`
- [ ] 7.4 Add usage instructions to `README.md`
- [ ] 7.5 Document common error patterns and resolutions

## 8. Code Quality
- [ ] 8.1 Add type hints to all functions (enforce with mypy)
- [ ] 8.2 Add docstrings to all public functions (Google style)
- [ ] 8.3 Run Black formatter (line length: 88)
- [ ] 8.4 Run isort for import organization
- [ ] 8.5 Run flake8 linter (max complexity: 10)
- [ ] 8.6 Verify PEP 8 compliance

## 9. Docker Integration
- [ ] 9.1 Update Dockerfile to install Docling dependencies
- [ ] 9.2 Add PDF processor service to `docker-compose.yml`
- [ ] 9.3 Test Docker build succeeds
- [ ] 9.4 Test volume mounts work correctly
- [ ] 9.5 Verify container can read PDFs and write CSVs
- [ ] 9.6 Add health check for PDF processor service

## 10. Validation & Deployment
- [ ] 10.1 Run full test suite and verify all tests pass
- [ ] 10.2 Test with real financial statement PDFs (at least 3 banks, 2 credit cards, 2 brokerages)
- [ ] 10.3 Verify failed PDFs move to `/data/failed/` with error logs
- [ ] 10.4 Verify successful PDFs move to `/data/processed/`
- [ ] 10.5 Verify CSVs in `/data/csv/` match expected schema
- [ ] 10.6 Run `openspec validate add-pdf-to-csv-extraction --strict`
- [ ] 10.7 Create PR for review
- [ ] 10.8 Update `CHANGELOG.md` with feature addition
