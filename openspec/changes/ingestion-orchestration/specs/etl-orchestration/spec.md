# Delta for ETL Orchestration

## ADDED Requirements

### Requirement: End-to-End ETL Pipeline Orchestration
The system SHALL orchestrate the complete ETL pipeline (Extract → Transform → Load) for financial statement PDFs.

#### Scenario: Successful PDF processing
- **GIVEN** a valid PDF in `/data/pdfs/` and account ID
- **WHEN** orchestrator executes
- **THEN** PDF SHALL be extracted to CSV (Extract phase)
- **AND** CSV SHALL be parsed and validated (Transform phase)
- **AND** transactions SHALL be loaded into database (Load phase)
- **AND** PDF SHALL be moved to `/data/processed/`
- **AND** import log SHALL be created with status="success"

#### Scenario: Extraction phase failure
- **GIVEN** a malformed PDF in `/data/pdfs/`
- **WHEN** orchestrator executes
- **THEN** extraction SHALL fail with error
- **AND** Transform and Load phases SHALL be skipped
- **AND** PDF SHALL be moved to `/data/failed/`
- **AND** error log SHALL be created with extraction error details

#### Scenario: Transform phase failure
- **GIVEN** a PDF that extracts to invalid CSV (missing columns)
- **WHEN** orchestrator executes
- **THEN** Extract phase SHALL succeed
- **AND** Transform phase SHALL fail with validation error
- **AND** Load phase SHALL be skipped
- **AND** PDF SHALL be moved to `/data/failed/`
- **AND** CSV SHALL be deleted (invalid data)

#### Scenario: Load phase failure
- **GIVEN** a valid PDF and CSV but database connection error
- **WHEN** orchestrator executes
- **THEN** Extract and Transform phases SHALL succeed
- **AND** Load phase SHALL fail with database error
- **AND** PDF SHALL remain in `/data/pdfs/` (not moved)
- **AND** transaction SHALL be rolled back (no partial data)
- **AND** user SHALL be able to retry after fixing database

### Requirement: Batch Processing of Multiple PDFs
The system SHALL process multiple PDFs in a single execution, continuing on individual failures.

#### Scenario: Mixed success and failure
- **GIVEN** 10 PDFs in `/data/pdfs/` (8 valid, 2 malformed)
- **WHEN** batch processing executes
- **THEN** all 10 PDFs SHALL be processed
- **AND** 8 valid PDFs SHALL succeed (moved to `/data/processed/`)
- **AND** 2 malformed PDFs SHALL fail (moved to `/data/failed/`)
- **AND** processing SHALL continue after each failure
- **AND** summary report SHALL show 8 succeeded, 2 failed

#### Scenario: Empty input directory
- **GIVEN** no PDFs in `/data/pdfs/`
- **WHEN** batch processing executes
- **THEN** processing SHALL complete without errors
- **AND** summary report SHALL show 0 processed

### Requirement: CLI for Manual Import Triggering
The system SHALL provide a command-line interface for users to trigger imports manually.

#### Scenario: Process command execution
- **GIVEN** PDFs in `/data/pdfs/` and account ID
- **WHEN** user runs `finance-import process --account-id=1`
- **THEN** all PDFs SHALL be processed
- **AND** progress indicator SHALL show "Processing X/Y PDFs..."
- **AND** summary report SHALL be printed
- **AND** exit code SHALL be 0 if all succeed, 1 if any fail

#### Scenario: Process command with dry-run
- **GIVEN** PDFs in `/data/pdfs/`
- **WHEN** user runs `finance-import process --account-id=1 --dry-run`
- **THEN** PDFs SHALL be extracted and parsed
- **AND** no database writes SHALL occur
- **AND** no files SHALL be moved
- **AND** summary report SHALL show what would be imported
- **AND** user can verify before committing

### Requirement: Import Status Reporting
The system SHALL provide status command to show import statistics.

#### Scenario: Status command execution
- **GIVEN** database with accounts and transactions
- **WHEN** user runs `finance-import status`
- **THEN** status SHALL display:
  - Total number of accounts
  - Total number of transactions
  - Last import date
  - Number of pending PDFs in `/data/pdfs/`

### Requirement: Account Creation via CLI
The system SHALL provide CLI command to create financial accounts.

#### Scenario: Create account command
- **GIVEN** account details (name, type, institution)
- **WHEN** user runs `finance-import create-account --name="Chase Checking" --type="checking" --institution="Chase Bank"`
- **THEN** account SHALL be created in database
- **AND** account ID SHALL be printed
- **AND** user can use account ID for imports

#### Scenario: Duplicate account name prevention
- **GIVEN** account "Chase Checking" already exists
- **WHEN** user tries to create another account with same name
- **THEN** creation SHALL fail with error "Account name already exists"
- **AND** no duplicate account SHALL be created

### Requirement: Error Isolation Between PDFs
The system SHALL isolate errors to individual PDFs, preventing one failure from stopping batch processing.

#### Scenario: Continue on failure
- **GIVEN** 5 PDFs (PDF1, PDF2-fail, PDF3, PDF4-fail, PDF5)
- **WHEN** batch processing executes
- **THEN** PDF1 SHALL succeed
- **AND** PDF2 SHALL fail (moved to `/data/failed/`)
- **AND** PDF3 SHALL succeed (processing continues)
- **AND** PDF4 SHALL fail (moved to `/data/failed/`)
- **AND** PDF5 SHALL succeed (processing continues)
- **AND** summary SHALL show 3 succeeded, 2 failed

### Requirement: Detailed Error Logging
The system SHALL log detailed error information for failed imports.

#### Scenario: Error log creation
- **GIVEN** a PDF that fails extraction
- **WHEN** processing fails
- **THEN** error log SHALL be created in `/data/failed/[pdf-name].error.log`
- **AND** error log SHALL include:
  - Timestamp
  - PDF filename
  - Phase that failed (Extract/Transform/Load)
  - Error message
  - Stack trace
- **AND** error log SHALL be in JSON format for parsing

### Requirement: Progress Indicators for User Feedback
The system SHALL display progress indicators during batch processing.

#### Scenario: Progress display
- **GIVEN** 10 PDFs to process
- **WHEN** batch processing executes
- **THEN** progress SHALL be displayed: "Processing 1/10 PDFs..."
- **AND** progress SHALL update for each PDF: "Processing 2/10 PDFs..."
- **AND** final summary SHALL be displayed after completion

#### Scenario: Verbose mode
- **GIVEN** verbose flag enabled
- **WHEN** processing executes
- **THEN** detailed logs SHALL be printed for each phase:
  - "Extracting: chase_statement.pdf"
  - "Parsing: chase_statement.csv (150 rows)"
  - "Loading: 145 transactions (5 duplicates skipped)"

### Requirement: Dry-Run Mode for Testing
The system SHALL support dry-run mode to simulate imports without making changes.

#### Scenario: Dry-run validation
- **GIVEN** PDFs in `/data/pdfs/`
- **WHEN** dry-run mode executes
- **THEN** PDFs SHALL be extracted to temporary directory
- **AND** CSVs SHALL be parsed and validated
- **AND** transaction hashes SHALL be checked for duplicates
- **AND** no database writes SHALL occur
- **AND** no files SHALL be moved
- **AND** summary SHALL show: "Would import 150 transactions (5 duplicates)"

### Requirement: Atomic PDF Processing
The system SHALL process each PDF atomically (all-or-nothing).

#### Scenario: Database rollback on failure
- **GIVEN** a PDF with 100 transactions, 50th transaction fails validation
- **WHEN** processing executes
- **THEN** first 49 transactions SHALL NOT be inserted
- **AND** database transaction SHALL be rolled back
- **AND** no partial data SHALL exist in database
- **AND** PDF SHALL be moved to `/data/failed/`

### Requirement: Dependency Injection for Testability
The system SHALL use dependency injection for orchestrator components.

#### Scenario: Orchestrator initialization
- **GIVEN** orchestrator dependencies (pdf_extractor, csv_parser, repositories)
- **WHEN** orchestrator is instantiated
- **THEN** all dependencies SHALL be passed via constructor
- **AND** no global state SHALL be used
- **AND** dependencies can be mocked for unit testing

### Requirement: Colored CLI Output for Readability
The system SHALL use colored output to highlight success and errors.

#### Scenario: Success output
- **GIVEN** successful import
- **WHEN** summary is printed
- **THEN** success messages SHALL be green
- **AND** counts SHALL be highlighted

#### Scenario: Error output
- **GIVEN** failed import
- **WHEN** summary is printed
- **THEN** error messages SHALL be red
- **AND** failed PDF paths SHALL be highlighted

### Requirement: Exit Code for Scripting
The system SHALL return appropriate exit codes for scripting integration.

#### Scenario: All PDFs succeed
- **GIVEN** all PDFs process successfully
- **WHEN** CLI exits
- **THEN** exit code SHALL be 0

#### Scenario: Any PDF fails
- **GIVEN** at least one PDF fails
- **WHEN** CLI exits
- **THEN** exit code SHALL be 1
- **AND** scripts can detect failure via exit code
