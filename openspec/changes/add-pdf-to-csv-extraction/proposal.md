# Proposal: PDF to CSV Extraction

## Why
Financial statement PDFs (bank statements, credit card statements, brokerage statements) need to be converted into structured CSV format for downstream processing in the ETL pipeline. Manual extraction is error-prone and doesn't scale across different financial institutions and statement formats.

## What Changes
- Add Docling-based PDF extraction module to convert financial statement PDFs into standardized CSV format
- Support multiple statement types: bank statements, credit card bills, and brokerage transaction histories
- Implement file system monitoring for PDF input directory (`/data/pdfs/`)
- Create validation layer to ensure CSV output meets required schema before database ingestion
- Add error handling for failed extractions with logging to separate directory (`/data/failed/`)
- Implement read-only processing (never modify original PDF files)

## Impact
- **Affected specs**: `pdf-extraction` (new capability), `etl-pipeline` (modified - adds Extract phase)
- **Affected code**: 
  - New module: `pdf_processor/` - Docling integration, file handlers, validators
  - Configuration: Docker Compose service definitions, environment variables for paths
  - Dependencies: `pyproject.toml` (add Docling library)
- **External dependencies**: Docling library for ML-based PDF document processing
- **Testing**: Unit tests for PDF validation, integration tests with sample financial statements from multiple institutions (banks, credit card issuers, brokerages)
