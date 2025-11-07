# Design: PDF to CSV Extraction

## Context
The finance dashboard ETL pipeline begins with financial statement PDFs that need structured extraction. Traditional PDF parsing libraries (PyPDF2, pdfplumber) require institution-specific regex patterns and brittle table extraction logic. Financial statement PDFs vary significantly by institution and type (Chase bank statements, American Express credit card bills, Fidelity brokerage statements, etc.) with complex layouts including multi-column tables, headers/footers, and inconsistent formatting.

**Constraints:**
- Privacy-first: No external API calls, all processing must be local
- Read-only: Original PDFs must never be modified
- Idempotent: Re-processing same PDF should not cause issues downstream
- File size: Support PDFs up to 50MB
- Python 3.11+ requirement

**Stakeholders:**
- End user: Expects reliable extraction from any US financial statement PDF (bank, credit card, brokerage)
- Downstream systems: CSV parser and database ingestion depend on consistent CSV schema

## Goals / Non-Goals

**Goals:**
- Extract transaction data from financial statement PDFs (bank, credit card, brokerage) into standardized CSV format
- Handle multiple statement types and layouts without custom per-institution parsers
- Provide clear error messages when extraction fails
- Organize files into appropriate directories based on processing outcome
- Enable testability with fixture PDFs from various financial institutions

**Non-Goals:**
- OCR for scanned/image-based PDFs (assume text-based PDFs only for v1)
- Real-time processing (batch processing is sufficient)
- PDF validation/repair (assume well-formed PDFs)
- Multi-language support (USD/English only for v1)
- GUI for manual review (filesystem-based workflow)

## Decisions

### Decision 1: Use Docling for PDF Extraction
**Choice:** Docling library with ML-based layout understanding

**Rationale:**
- Modern ML-based approach handles varied layouts better than regex
- Direct PDF-to-CSV conversion reduces custom parsing code
- Better table extraction for financial data (amount columns, date alignment)
- Adapts to layout changes without code modifications

**Alternatives Considered:**
1. **PyPDF2** - Too low-level, no table extraction, requires extensive custom code
2. **pdfplumber** - Good table detection but needs bank-specific tuning, manual column mapping
3. **Camelot** - Strong table extraction but requires Java dependency (Tabula), harder to containerize
4. **Custom regex parsers** - Brittle, maintenance nightmare across bank formats

**Why Docling wins:** Balances extraction quality with maintenance burden. ML-based approach generalizes better across financial statement formats (bank, credit card, brokerage).

### Decision 2: File System Organization
**Choice:** Separate directories for input, intermediate, processed, and failed files

**Directory Structure:**
```
/data/
├── pdfs/         # Input: User places PDFs here
├── csv/          # Intermediate: Extracted CSVs before validation
├── processed/    # Success: Original PDFs moved here after ingestion
└── failed/       # Failure: PDFs that couldn't be extracted
```

**Rationale:**
- Clear visual status of each file's processing state
- Original PDFs preserved in either `processed/` or `failed/`
- CSV files in staging area allow manual inspection before ingestion
- Failed PDFs isolated for manual review

### Decision 3: CSV Schema Standardization
**Choice:** Fixed CSV schema with required columns

**Required Columns:**
- `transaction_date` (YYYY-MM-DD)
- `posting_date` (YYYY-MM-DD, optional)
- `description` (text)
- `amount` (decimal, negative for expenses)
- `balance` (decimal, optional running balance)
- `transaction_type` (debit/credit)

**Rationale:**
- Consistent schema simplifies downstream CSV parser
- Validation layer catches extraction errors before database
- Optional fields handle varying bank statement detail levels

### Decision 4: Error Handling Strategy
**Choice:** Fail-fast with detailed logging, no auto-correction

**Approach:**
- PDF extraction failures logged with error details
- Failed PDFs moved to `/data/failed/` with `.error.log` companion file
- No automatic retries (user intervention required)
- Validation errors prevent CSV promotion to database ingestion

**Rationale:**
- Financial data requires manual verification of failures
- Auto-correction risks data integrity (incorrect amounts)
- Clear error logs enable user troubleshooting

## Implementation Architecture

### Module Structure
```python
pdf_processor/
├── __init__.py
├── extractor.py          # Docling integration
├── validator.py          # CSV schema validation
├── file_handler.py       # File operations (read, move, organize)
├── models.py             # Pydantic models for CSV schema
└── exceptions.py         # Custom exceptions
```

### Core Classes

**PDFExtractor:**
- Responsibility: Convert PDF to CSV using Docling
- Methods: `extract(pdf_path: Path) -> Path` (returns CSV path)
- Error handling: Raises `ExtractionError` on failure

**CSVValidator:**
- Responsibility: Validate CSV against required schema
- Methods: `validate(csv_path: Path) -> ValidationResult`
- Checks: Required columns, data types, date formats, amount precision

**FileHandler:**
- Responsibility: File system operations (read-only PDFs)
- Methods: `move_to_processed()`, `move_to_failed()`, `list_pending_pdfs()`
- Safety: Never modifies original PDFs, atomic moves

### Processing Flow
```
1. Scan /data/pdfs/ for new PDFs
2. For each PDF:
   a. Extract to /data/csv/ (Docling)
   b. Validate CSV schema
   c. If valid: move PDF to /data/processed/
   d. If invalid: move PDF to /data/failed/ with error log
3. CSV files in /data/csv/ ready for ingestion pipeline
```

## Risks / Trade-offs

### Risk 1: Docling Extraction Accuracy
**Risk:** Docling may misinterpret complex PDF layouts (merged cells, split transactions, varying statement formats)

**Mitigation:**
- Comprehensive test suite with real financial statements from 5+ institutions (banks, credit card issuers, brokerages)
- Validation layer catches extraction errors before database
- Failed PDFs logged for manual review and pattern analysis
- Iterative Docling configuration tuning based on failure patterns

### Risk 2: Large PDF Performance
**Risk:** 50MB PDFs may cause memory issues or slow processing

**Mitigation:**
- Process PDFs one at a time (no parallel processing in v1)
- Docker container memory limits prevent system-wide impact
- Timeout handling (30 second limit per PDF)
- Large files that fail moved to `/data/failed/` for investigation

### Risk 3: CSV Schema Evolution
**Risk:** Financial statement formats change, requiring schema updates

**Mitigation:**
- Pydantic models enable easy schema versioning
- Validation errors clearly indicate missing/unexpected columns
- Failed extractions provide feedback for schema adjustments
- Schema version tracked in CSV metadata (future enhancement)

### Trade-off 1: No OCR Support
**Accepted:** Scanned/image PDFs will fail extraction

**Justification:** 
- Vast majority of modern bank statements are text-based PDFs
- OCR adds significant complexity (Tesseract dependency, accuracy issues)
- Can be added in future enhancement if needed
- Users can identify image PDFs from validation errors

### Trade-off 2: Batch vs Real-time Processing
**Accepted:** Files processed in batches, not immediately on upload

**Justification:**
- Simplifies implementation (no file system watchers, no concurrency)
- Aligns with manual upload workflow (user places multiple PDFs, runs import)
- Scheduled processing acceptable for personal finance use case
- Real-time processing can be added later with APScheduler

## Migration Plan

**Initial Setup:**
1. Create directory structure: `/data/{pdfs,csv,processed,failed}/`
2. Add Docling to `pyproject.toml` dependencies
3. Build Docker image with `uv pip install` including Docling
4. Configure environment variables for directory paths in `.env`
5. Add volume mounts for `/data/` in `docker-compose.yml`

**Testing Approach:**
1. Create test fixtures: 5-10 anonymized financial statement PDFs (Chase/BoA bank statements, Amex/Visa credit cards, Fidelity/Schwab brokerage)
2. Unit tests: Validator logic, file handler operations
3. Integration tests: End-to-end PDF → CSV → validation flow
4. Fixture-based tests: Verify extraction accuracy per institution and statement type

**Rollback:**
- No database changes in this phase (pure file processing)
- Remove `pdf_processor/` module and revert dependencies
- Delete `/data/` directory structure
- No data migration needed (feature addition, not modification)

## Open Questions

1. **CSV encoding:** UTF-8 with BOM or without? (Decision: UTF-8 without BOM for POSIX compatibility)
2. **Duplicate PDFs:** Should we hash PDFs to detect re-uploads? (Decision: Defer to downstream deduplication via transaction hashing)
3. **Partial extraction:** If Docling extracts 80% of transactions, accept or reject? (Decision: Reject - require 100% extraction or manual review)
4. **Multi-page statements:** How to handle statements spanning 10+ pages? (Decision: Docling handles multi-page naturally, validate total transaction count matches statement summary if present)
5. **Date parsing ambiguity:** US (MM/DD/YYYY) vs international (DD/MM/YYYY)? (Decision: Assume US format, add configuration option in future if needed)
