# Capability: PDF Extraction

## ADDED Requirements

### Requirement: Extract Transactions from PDF Financial Statements
The system SHALL extract transaction data from financial statement PDFs (bank statements, credit card statements, brokerage statements) and convert them into standardized CSV format using Docling library.

#### Scenario: Successful PDF extraction
- **GIVEN** a valid text-based financial statement PDF in `/data/pdfs/` directory
- **WHEN** the PDF processor executes extraction
- **THEN** a CSV file SHALL be created in `/data/csv/` with required columns
- **AND** the CSV SHALL contain all transactions from the PDF
- **AND** the original PDF SHALL be moved to `/data/processed/` directory
- **AND** the original PDF SHALL remain unmodified

#### Scenario: Failed PDF extraction
- **GIVEN** a malformed or image-based PDF in `/data/pdfs/` directory
- **WHEN** the PDF processor attempts extraction
- **THEN** extraction SHALL fail with a descriptive error message
- **AND** the PDF SHALL be moved to `/data/failed/` directory
- **AND** an error log file SHALL be created alongside the failed PDF
- **AND** the error log SHALL contain extraction failure details

#### Scenario: Large PDF handling
- **GIVEN** a financial statement PDF larger than 10MB but under 50MB
- **WHEN** the PDF processor executes extraction
- **THEN** extraction SHALL complete within 30 seconds timeout
- **AND** extraction SHALL handle the file without memory errors
- **OR** if timeout exceeded, the PDF SHALL be moved to `/data/failed/` with timeout error

### Requirement: CSV Schema Standardization
The system SHALL produce CSV files with a standardized schema containing required financial transaction columns.

#### Scenario: Valid CSV output
- **GIVEN** a successfully extracted PDF
- **WHEN** CSV validation executes
- **THEN** the CSV SHALL contain required columns: `transaction_date`, `description`, `amount`, `transaction_type`
- **AND** the CSV MAY contain optional columns: `posting_date`, `balance`
- **AND** `transaction_date` SHALL be in YYYY-MM-DD format
- **AND** `amount` SHALL be a decimal number with 2 decimal places
- **AND** `transaction_type` SHALL be either "debit" or "credit"

#### Scenario: Invalid CSV schema
- **GIVEN** a CSV file missing required columns
- **WHEN** CSV validation executes
- **THEN** validation SHALL fail with specific missing column errors
- **AND** the corresponding PDF SHALL be moved to `/data/failed/`
- **AND** the invalid CSV SHALL be deleted from `/data/csv/`

### Requirement: File System Organization
The system SHALL organize PDF files into appropriate directories based on processing outcome while maintaining read-only access to originals.

#### Scenario: Directory structure initialization
- **GIVEN** the PDF processor starts for the first time
- **WHEN** initialization executes
- **THEN** directories SHALL be created: `/data/pdfs/`, `/data/csv/`, `/data/processed/`, `/data/failed/`
- **AND** all directories SHALL have appropriate read/write permissions

#### Scenario: Successful file organization
- **GIVEN** a PDF successfully extracted and validated
- **WHEN** file organization executes
- **THEN** the original PDF SHALL be moved from `/data/pdfs/` to `/data/processed/`
- **AND** the move SHALL be atomic (no partial file states)
- **AND** the original PDF filename SHALL be preserved

#### Scenario: Failed file organization
- **GIVEN** a PDF that failed extraction or validation
- **WHEN** file organization executes
- **THEN** the original PDF SHALL be moved from `/data/pdfs/` to `/data/failed/`
- **AND** an error log file SHALL be created with `.error.log` extension
- **AND** the error log SHALL contain timestamp, error type, and details

### Requirement: Read-Only PDF Processing
The system SHALL never modify original PDF files during extraction or processing operations.

#### Scenario: PDF integrity verification
- **GIVEN** any PDF in the processing pipeline
- **WHEN** extraction, validation, or file operations execute
- **THEN** the PDF file content SHALL remain byte-identical to the original
- **AND** the PDF file metadata (creation date, permissions) SHALL be preserved during moves

### Requirement: Batch Processing Support
The system SHALL support batch processing of multiple PDF files in a single execution.

#### Scenario: Multiple PDFs processed
- **GIVEN** 5 PDF files in `/data/pdfs/` directory
- **WHEN** batch processing executes
- **THEN** all 5 PDFs SHALL be processed sequentially
- **AND** a summary report SHALL be generated with counts: processed, failed, total
- **AND** processing SHALL continue even if individual PDFs fail

#### Scenario: Empty input directory
- **GIVEN** no PDF files in `/data/pdfs/` directory
- **WHEN** batch processing executes
- **THEN** processing SHALL complete without errors
- **AND** a message SHALL indicate no PDFs found

### Requirement: Extraction Timeout Handling
The system SHALL enforce timeout limits on PDF extraction to prevent indefinite hanging on problematic files.

#### Scenario: Extraction timeout exceeded
- **GIVEN** a PDF that takes longer than 30 seconds to process
- **WHEN** extraction executes
- **THEN** extraction SHALL be terminated after 30 seconds
- **AND** the PDF SHALL be marked as failed with timeout error
- **AND** the PDF SHALL be moved to `/data/failed/` directory

### Requirement: Comprehensive Error Logging
The system SHALL log all extraction failures with sufficient detail for troubleshooting and analysis.

#### Scenario: Error log creation
- **GIVEN** a PDF extraction failure of any type
- **WHEN** error handling executes
- **THEN** an error log SHALL be created with structured JSON format
- **AND** the log SHALL include: timestamp, PDF filename, error type, error message, stack trace
- **AND** the log SHALL be written to `/data/failed/[pdf-name].error.log`

### Requirement: CSV Validation Before Ingestion
The system SHALL validate CSV output against the required schema before allowing downstream database ingestion.

#### Scenario: Validation prevents invalid data ingestion
- **GIVEN** a CSV file with missing required columns
- **WHEN** validation executes
- **THEN** the CSV SHALL NOT be available for database ingestion
- **AND** validation errors SHALL be logged
- **AND** the source PDF SHALL be moved to `/data/failed/`

#### Scenario: Validation approves valid data
- **GIVEN** a CSV file with all required columns and valid data types
- **WHEN** validation executes
- **THEN** the CSV SHALL remain in `/data/csv/` for ingestion
- **AND** validation success SHALL be logged

### Requirement: Support Multiple Financial Statement Formats
The system SHALL handle financial statement PDFs from different institutions and statement types without requiring custom parsers per institution.

#### Scenario: Multi-institution extraction
- **GIVEN** PDF statements from Chase Bank, American Express credit card, and Fidelity brokerage
- **WHEN** extraction executes on each PDF
- **THEN** all PDFs SHALL be extracted using the same Docling-based extractor
- **AND** CSV outputs SHALL conform to the same standardized schema
- **AND** no institution-specific code branches SHALL be required

### Requirement: Idempotent Processing
The system SHALL handle re-processing of the same PDF without causing duplicate records or errors.

#### Scenario: Duplicate PDF detection
- **GIVEN** a PDF that was previously processed successfully
- **WHEN** the same PDF is placed in `/data/pdfs/` again
- **THEN** extraction SHALL proceed normally
- **AND** the CSV SHALL be regenerated
- **AND** downstream deduplication (via transaction hashing) SHALL prevent duplicate database records

### Requirement: Memory Efficient Processing
The system SHALL process PDFs within defined memory limits to prevent system resource exhaustion.

#### Scenario: Memory limit enforcement
- **GIVEN** Docker container memory limit of 1GB
- **WHEN** large PDF extraction executes
- **THEN** extraction SHALL remain within memory constraints
- **OR** if memory exceeded, extraction SHALL fail gracefully with memory error
- **AND** the system SHALL not crash or hang

### Requirement: CLI Interface for Manual Execution
The system SHALL provide a command-line interface for users to manually trigger PDF processing.

#### Scenario: Manual processing trigger
- **GIVEN** PDFs in `/data/pdfs/` directory
- **WHEN** user executes `python -m pdf_processor.cli process`
- **THEN** batch processing SHALL execute
- **AND** progress SHALL be displayed to stdout
- **AND** summary report SHALL be printed upon completion

#### Scenario: Dry-run mode
- **GIVEN** PDFs in `/data/pdfs/` directory
- **WHEN** user executes `python -m pdf_processor.cli process --dry-run`
- **THEN** extraction SHALL be simulated without moving files
- **AND** validation SHALL execute on simulated CSVs
- **AND** a report SHALL show what would happen without making changes
