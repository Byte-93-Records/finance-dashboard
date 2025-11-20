# PDF to CSV Extraction Walkthrough

## Overview
I have implemented the PDF to CSV extraction feature for the Finance Dashboard. This feature allows you to place financial statement PDFs in a directory and automatically convert them to structured CSV files for analysis.

## Changes Implemented

### 1. Core Module (`pdf_processor`)
- **`extractor.py`**: Implemented `PDFExtractor` using Docling to extract tables from PDFs.
- **`validator.py`**: Implemented `CSVValidator` to ensure extracted data matches the required schema.
- **`file_handler.py`**: Implemented `FileHandler` to manage file movements (processing -> processed/failed).
- **`models.py`**: Defined Pydantic models for data structure.
- **`exceptions.py`**: Defined custom exceptions for error handling.
- **`cli.py`**: Created a command-line interface to orchestrate the process.

### 2. Docker Integration
- **`Dockerfile`**: Created a Dockerfile to build the application with all dependencies.
- **`docker-compose.yml`**: Configured the `pdf-processor` service with volume mounts.

### 3. Testing
- **Unit Tests**: Added tests for `CSVValidator` and `FileHandler`.
- **Integration Tests**: Added tests for `PDFExtractor` (mocked).
- **End-to-End Tests**: Added tests for the full CLI flow.
- **Verification**: All tests passed in both local and Docker environments.

## How to Use

### 1. Start the Services
```bash
docker compose up -d
```

### 2. Process PDFs
Place your PDF statements in `data/pdfs/`.
Then run the processor:
```bash
docker compose exec pdf-processor python -m pdf_processor.cli process
```

### 3. Check Results
- **Success**: CSV files will be in `data/csv/` and PDFs moved to `data/processed/`.
- **Failure**: Failed PDFs will be in `data/failed/` with an error log.

## Verification Results
Ran full test suite in Docker:
```
tests/pdf_processor/test_e2e.py ...
tests/pdf_processor/test_extractor.py ...
tests/pdf_processor/test_file_handler.py ...
tests/pdf_processor/test_validator.py .....
14 passed
```
