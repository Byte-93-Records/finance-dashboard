# Spec: Data Architecture for Scale

## ADDED Requirements

### Requirement: Raw Data Layer
The system SHALL maintain an immutable raw transactions table partitioned by year.

#### Scenario: Transaction partitioning
- **GIVEN** transactions from 2024 and 2025
- **WHEN** tables are partitioned
- **THEN** data splits into `transactions_2024` and `transactions_2025`

#### Scenario: Import tracking
- **GIVEN** a batch of 100 PDFs imported
- **WHEN** import completes
- **THEN** each transaction has `import_id` linking to `import_logs` entry

#### Scenario: Deduplication preserved
- **GIVEN** the same PDF imported twice
- **WHEN** second import runs
- **THEN** duplicates are skipped (hash-based deduplication still works)

---

### Requirement: Daily Summary View
The system SHALL provide aggregated daily spending via materialized view.

#### Scenario: Daily aggregation
- **GIVEN** 10 transactions on 2025-01-07 (5 from account A, 5 from account B)
- **WHEN** daily_summary is queried
- **THEN** one row per account per date with total spending amount

#### Scenario: View refresh after import
- **GIVEN** new transactions imported
- **WHEN** import completes
- **THEN** daily_summary automatically refreshed with new data

---

### Requirement: Monthly Summary View
The system SHALL provide aggregated monthly spending with category breakdown via materialized view.

#### Scenario: Monthly aggregation
- **GIVEN** 100 transactions across all accounts in January 2025
- **WHEN** monthly_summary is queried
- **THEN** one row per account per category with total spending

#### Scenario: Category field
- **GIVEN** transactions with NULL category (existing data)
- **WHEN** queries reference category
- **THEN** NULL values treated as "Uncategorized"

---

### Requirement: Merchant Summary View
The system SHALL provide top merchants by spending via materialized view.

#### Scenario: Top merchants ranking
- **GIVEN** transactions from 100 merchants
- **WHEN** merchant_summary is queried
- **THEN** returns top 100 merchants sorted by total spending descending

#### Scenario: Merchant aggregation
- **GIVEN** 50 transactions to "AMAZON.COM"
- **WHEN** merchant_summary is generated
- **THEN** all Amazon transactions summed into single row

---

### Requirement: Import Logs Table
The system SHALL track each import batch for audit and resume capability.

#### Scenario: Import tracking
- **GIVEN** a batch of 50 PDFs processed
- **WHEN** import completes
- **THEN** import_logs records: timestamp, file_count, transaction_count, status

#### Scenario: Import identification
- **GIVEN** duplicate import attempt
- **WHEN** system checks import_logs
- **THEN** can identify and skip already-processed files

---

### Requirement: Schema Backward Compatibility
The system SHALL maintain existing transaction structure while adding new columns.

#### Scenario: Existing queries still work
- **GIVEN** existing Grafana dashboards querying transactions
- **WHEN** schema migration runs
- **THEN** all existing columns and queries unaffected

#### Scenario: Category column added
- **GIVEN** existing transactions without category
- **WHEN** category column added
- **THEN** values default to NULL (safe to add)

---

## MODIFIED Requirements

### Requirement: Transaction Storage
The system SHALL store transactions with enhanced metadata.

**Updated:**
- Add `category` column (VARCHAR, nullable)
- Add `import_id` foreign key to `import_logs`
- Partition table by transaction year

**Rationale:**
- `category` prepares for future categorization (v0.3)
- `import_id` enables audit trail and duplicate detection
- Partitioning improves query performance on large tables
