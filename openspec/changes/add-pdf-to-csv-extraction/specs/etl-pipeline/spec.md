# Capability: ETL Pipeline

## ADDED Requirements

### Requirement: PDF Extraction Phase Integration
The ETL pipeline SHALL incorporate PDF extraction as the initial Extract phase before CSV parsing and database loading.

#### Scenario: Complete ETL flow with PDF input
- **GIVEN** financial statement PDFs in `/data/pdfs/` directory
- **WHEN** ETL pipeline executes
- **THEN** Extract phase SHALL convert PDFs to CSVs in `/data/csv/`
- **AND** Transform phase SHALL parse and validate CSV data
- **AND** Load phase SHALL insert transactions into PostgreSQL database
- **AND** each phase SHALL complete before the next begins

#### Scenario: ETL phase failure handling
- **GIVEN** a PDF extraction failure in the Extract phase
- **WHEN** ETL pipeline processes the failed PDF
- **THEN** the failed PDF SHALL be isolated in `/data/failed/`
- **AND** other PDFs SHALL continue processing
- **AND** Transform and Load phases SHALL only process successfully extracted CSVs

### Requirement: Extract Phase Configuration
The ETL pipeline SHALL provide configuration for the PDF extraction phase including directory paths and processing parameters.

#### Scenario: Extract phase configuration via environment variables
- **GIVEN** environment variables for PDF directories
- **WHEN** ETL pipeline initializes
- **THEN** Extract phase SHALL use configured paths: `PDF_INPUT_DIR`, `CSV_OUTPUT_DIR`, `PROCESSED_DIR`, `FAILED_DIR`
- **AND** Extract phase SHALL use configured timeout: `PDF_TIMEOUT_SECONDS`
- **AND** invalid configuration SHALL prevent pipeline startup with clear error messages

### Requirement: Extract Phase Monitoring
The ETL pipeline SHALL provide observability into the PDF extraction phase including success/failure rates and processing times.

#### Scenario: Extraction metrics collection
- **GIVEN** batch processing of 10 PDFs
- **WHEN** ETL pipeline completes
- **THEN** metrics SHALL be logged: total processed, successful extractions, failed extractions
- **AND** metrics SHALL include: average processing time per PDF, total processing time
- **AND** metrics SHALL be structured (JSON) for parsing by monitoring systems

## MODIFIED Requirements

### Requirement: ETL Pipeline Architecture
The ETL pipeline SHALL follow a three-phase architecture: Extract (PDF) → Transform (CSV parsing) → Load (PostgreSQL).

**Previous behavior:** ETL started with CSV files as input  
**New behavior:** ETL starts with PDF files, converts to CSV, then proceeds with Transform/Load phases

#### Scenario: Three-phase execution order
- **GIVEN** the ETL pipeline is invoked
- **WHEN** execution begins
- **THEN** Extract phase SHALL execute first (PDF → CSV)
- **AND** Transform phase SHALL execute second (CSV parsing and validation)
- **AND** Load phase SHALL execute third (PostgreSQL insertion)
- **AND** each phase SHALL complete successfully before the next begins
- **AND** failure in any phase SHALL halt remaining phases for that file

### Requirement: Input Data Format
The ETL pipeline SHALL accept financial statement PDFs as primary input format, with CSVs supported for legacy/manual workflows.

**Previous behavior:** Only CSV files were accepted as input  
**New behavior:** PDFs are primary input, CSVs in `/data/csv/` can still be processed directly (skipping Extract phase)

#### Scenario: PDF input processing
- **GIVEN** PDF files in `/data/pdfs/`
- **WHEN** ETL pipeline executes
- **THEN** PDFs SHALL be processed through all three phases

#### Scenario: Direct CSV input (legacy support)
- **GIVEN** CSV files directly placed in `/data/csv/` (no corresponding PDF)
- **WHEN** ETL pipeline executes
- **THEN** CSVs SHALL be processed through Transform and Load phases only
- **AND** Extract phase SHALL be skipped for these files
