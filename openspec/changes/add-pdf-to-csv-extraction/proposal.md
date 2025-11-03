# Proposal: PDF to CSV Extraction

## Why
Bank statement PDFs need to be converted into structured CSV format for downstream processing in the ETL pipeline. Manual extraction is error-prone and doesn't scale across different bank statement formats.

## What Changes
- Add Docling-based PDF extraction module to convert bank statement PDFs into standardized CSV format
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
- **Testing**: Unit tests for PDF validation, integration tests with sample bank PDFs from multiple institutions
