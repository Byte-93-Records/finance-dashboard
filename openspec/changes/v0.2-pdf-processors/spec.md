# Spec: Bank-Specific PDF Processors

## ADDED Requirements

### Requirement: PDF Router
The system SHALL route PDF files to bank-specific processors based on filename.

#### Scenario: Amex PDF routing
- **GIVEN** a PDF named `amex_bluecash_01_2024.pdf`
- **WHEN** the router processes it
- **THEN** AmexProcessor is selected

#### Scenario: Chase PDF routing
- **GIVEN** a PDF named `chase_sapphire_03_2024.pdf`
- **WHEN** the router processes it
- **THEN** ChaseProcessor is selected

#### Scenario: Unknown bank fallback
- **GIVEN** a PDF named `unknown_bank_01_2024.pdf`
- **WHEN** the router processes it
- **THEN** GenericProcessor (Docling) is selected

---

### Requirement: Amex Processor
The system SHALL extract transactions from Amex PDF statements using pdfplumber.

#### Scenario: Multi-line description handling
- **GIVEN** an Amex PDF with a transaction description wrapped across 2 lines
- **WHEN** extracted
- **THEN** the description is joined into a single line

#### Scenario: Amex yearly statement
- **GIVEN** an Amex yearly statement PDF (12 months, 300+ transactions)
- **WHEN** extracted
- **THEN** all transactions are extracted with correct dates and amounts

#### Scenario: Amex amount parsing
- **GIVEN** an Amex transaction showing "$1,234.56"
- **WHEN** extracted
- **THEN** amount is stored as `1234.56` (decimal, no currency symbol)

---

### Requirement: Chase Processor
The system SHALL extract transactions from Chase PDF statements.

#### Scenario: Chase credit card statement
- **GIVEN** a Chase credit card PDF
- **WHEN** extracted
- **THEN** transactions are extracted with date, description, and amount

#### Scenario: Chase date format
- **GIVEN** a Chase transaction dated "01/15"
- **WHEN** extracted
- **THEN** date is converted to `2024-01-15` (year inferred from statement)

---

### Requirement: Generic Processor Fallback
The system SHALL fall back to Docling extraction for unrecognized banks.

#### Scenario: Existing behavior preserved
- **GIVEN** a Citi PDF that currently processes successfully
- **WHEN** processed with new router
- **THEN** extraction succeeds with identical output

#### Scenario: Unknown bank handled
- **GIVEN** a PDF from an unsupported bank
- **WHEN** processed
- **THEN** GenericProcessor attempts extraction (may succeed or fail gracefully)

---

### Requirement: Consistent CSV Output
All processors SHALL output CSV with the standard schema.

#### Scenario: Schema compliance
- **GIVEN** any processor extracts a PDF
- **WHEN** CSV is generated
- **THEN** it contains columns: `transaction_date`, `description`, `amount`, `transaction_type`

#### Scenario: Amount precision
- **GIVEN** a transaction amount
- **WHEN** written to CSV
- **THEN** amount has exactly 2 decimal places

---

### Requirement: Extraction Failure Handling
The system SHALL handle extraction failures gracefully.

#### Scenario: Processor failure
- **GIVEN** a PDF that causes processor to fail
- **WHEN** extraction is attempted
- **THEN** PDF is moved to `failed/` directory with error log

#### Scenario: Batch continues on failure
- **GIVEN** a batch of 10 PDFs where 1 fails
- **WHEN** batch processing runs
- **THEN** remaining 9 PDFs are still processed
