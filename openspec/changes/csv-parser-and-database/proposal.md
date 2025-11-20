# Proposal: CSV Parser and Database Schema

## Why
The PDF extraction phase (Extract) is complete. Now we need to:
1. **Transform Phase**: Parse and validate CSV files to ensure data quality before database ingestion
2. **Load Phase**: Define database schema and implement data loading into PostgreSQL

This completes the ETL pipeline: Extract (PDF → CSV) → Transform (CSV parsing) → Load (PostgreSQL).

## What Changes
### CSV Parser Module (`csv_parser/`)
- Parse standardized CSV files from PDF extraction
- Validate transaction data (dates, amounts, types)
- Normalize transaction descriptions
- Handle edge cases (multi-line descriptions, split transactions)
- Convert CSV rows into domain models for database ingestion

### Database Schema (`database/`)
- SQLAlchemy models for core tables:
  - `accounts` - Financial account information
  - `transactions` - Individual transactions with hash-based deduplication
  - `categories` - Transaction categorization (optional for v1)
  - `import_logs` - Track PDF import history
- Alembic migrations for schema versioning
- Repository pattern for data access

### Ingestion Orchestration (`ingestion/`)
- Orchestrate the full ETL pipeline
- Coordinate PDF extraction → CSV parsing → database loading
- Handle errors at each phase
- Provide summary reporting

## Impact
- **Affected specs**: `etl-pipeline` (completes all three phases), `csv-parsing` (new), `database-schema` (new)
- **Affected code**: 
  - New modules: `csv_parser/`, `database/`, `ingestion/`
  - Configuration: Database connection strings, Alembic setup
  - Dependencies: SQLAlchemy, Alembic, psycopg2
- **External dependencies**: PostgreSQL 18 (via Docker)
- **Testing**: Unit tests for CSV parsing, integration tests with test database

## Next Steps
1. Create detailed design and specs for CSV parser
2. Define database schema (tables, relationships, indexes)
3. Implement CSV parser with validation
4. Implement database models and repositories
5. Create Alembic migrations
6. Build ingestion orchestrator
7. End-to-end testing with sample PDFs
