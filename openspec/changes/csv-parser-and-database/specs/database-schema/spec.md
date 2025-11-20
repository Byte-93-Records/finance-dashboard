# Delta for Database Schema

## ADDED Requirements

### Requirement: PostgreSQL Database Schema for Financial Transactions
The system SHALL define a normalized PostgreSQL database schema to store financial accounts, transactions, categories, and import logs.

#### Scenario: Database initialization
- **GIVEN** a fresh PostgreSQL database
- **WHEN** Alembic migrations execute
- **THEN** four tables SHALL be created: `accounts`, `transactions`, `categories`, `import_logs`
- **AND** all foreign key constraints SHALL be created
- **AND** all indexes SHALL be created
- **AND** all check constraints SHALL be created

### Requirement: Accounts Table
The system SHALL provide an `accounts` table to store financial account information.

#### Scenario: Account creation
- **GIVEN** account data (name="Chase Checking", account_type="checking", institution="Chase Bank")
- **WHEN** account is created via `AccountRepository.create()`
- **THEN** account SHALL be inserted into `accounts` table
- **AND** account SHALL have auto-generated `id` (SERIAL PRIMARY KEY)
- **AND** account SHALL have `created_at` timestamp (default NOW())

#### Scenario: Account types validation
- **GIVEN** account with account_type value
- **WHEN** account is created
- **THEN** account_type SHALL be one of: "checking", "savings", "credit_card", "brokerage"
- **AND** invalid account_type SHALL fail with constraint violation

### Requirement: Transactions Table
The system SHALL provide a `transactions` table to store financial transactions with deduplication support.

#### Scenario: Transaction creation
- **GIVEN** transaction data (account_id, transaction_date, description, amount, transaction_type)
- **WHEN** transaction is created via `TransactionRepository.create()`
- **THEN** transaction SHALL be inserted into `transactions` table
- **AND** transaction SHALL have auto-generated `id` (SERIAL PRIMARY KEY)
- **AND** transaction SHALL have `transaction_hash` (SHA-256 hash for deduplication)
- **AND** transaction SHALL have `created_at` timestamp (default NOW())

#### Scenario: Transaction amount precision
- **GIVEN** transaction with amount 123.456 (3 decimal places)
- **WHEN** transaction is inserted
- **THEN** amount SHALL be stored as NUMERIC(12,2)
- **AND** amount SHALL be rounded to 123.46 (2 decimal places)
- **AND** no float rounding errors SHALL occur

#### Scenario: Transaction type validation
- **GIVEN** transaction with transaction_type value
- **WHEN** transaction is inserted
- **THEN** transaction_type SHALL be either "debit" or "credit"
- **AND** invalid transaction_type SHALL fail with check constraint violation

#### Scenario: Foreign key constraint on account_id
- **GIVEN** transaction with account_id=999 (non-existent account)
- **WHEN** transaction is inserted
- **THEN** insert SHALL fail with foreign key constraint violation
- **AND** error message SHALL indicate account does not exist

#### Scenario: Cascade delete on account
- **GIVEN** an account with 100 transactions
- **WHEN** account is deleted
- **THEN** all 100 transactions SHALL be deleted (CASCADE)
- **AND** no orphaned transactions SHALL remain

### Requirement: Transaction Hash Uniqueness for Deduplication
The system SHALL enforce unique transaction hashes to prevent duplicate transactions.

#### Scenario: Duplicate transaction prevention
- **GIVEN** a transaction with hash "abc123..." already exists in database
- **WHEN** another transaction with same hash is inserted
- **THEN** insert SHALL fail with unique constraint violation
- **AND** duplicate transaction SHALL NOT be inserted

#### Scenario: Hash generation determinism
- **GIVEN** two identical transactions (same account_id, date, amount, description)
- **WHEN** transaction hashes are generated
- **THEN** both hashes SHALL be identical
- **AND** second transaction SHALL be rejected as duplicate

### Requirement: Transaction Indexes for Query Performance
The system SHALL provide indexes on `transactions` table to optimize common queries.

#### Scenario: Query by transaction date
- **GIVEN** 10,000 transactions in database
- **WHEN** querying transactions by date range (e.g., "2024-01-01" to "2024-01-31")
- **THEN** query SHALL use `idx_transactions_date` index
- **AND** query SHALL complete in < 100ms

#### Scenario: Query by account and date
- **GIVEN** 10,000 transactions across 5 accounts
- **WHEN** querying transactions for specific account and date range
- **THEN** query SHALL use `idx_transactions_account_date` composite index
- **AND** query SHALL complete in < 100ms

### Requirement: Categories Table for Transaction Categorization
The system SHALL provide a `categories` table to support transaction categorization.

#### Scenario: Category creation
- **GIVEN** category data (name="Groceries")
- **WHEN** category is created
- **THEN** category SHALL be inserted into `categories` table
- **AND** category name SHALL be unique
- **AND** duplicate category name SHALL fail with unique constraint violation

#### Scenario: Category hierarchy support
- **GIVEN** parent category "Dining" and child category "Fast Food"
- **WHEN** child category is created with parent_id
- **THEN** child category SHALL reference parent category via `parent_id` foreign key
- **AND** parent category deletion SHALL set child `parent_id` to NULL (ON DELETE SET NULL)

#### Scenario: Optional category assignment
- **GIVEN** a transaction without category
- **WHEN** transaction is created
- **THEN** transaction `category_id` SHALL be NULL
- **AND** transaction SHALL be valid without category

### Requirement: Import Logs Table for Audit Trail
The system SHALL provide an `import_logs` table to track PDF import history.

#### Scenario: Import log creation
- **GIVEN** successful CSV import (filename="chase_2024-01.csv", records_imported=150, records_skipped=5)
- **WHEN** import log is created
- **THEN** import log SHALL be inserted into `import_logs` table
- **AND** import log SHALL have status="success"
- **AND** import log SHALL have `import_date` timestamp (default NOW())
- **AND** import log SHALL have `file_hash` (SHA-256 of original PDF)

#### Scenario: Failed import logging
- **GIVEN** failed CSV import (validation errors)
- **WHEN** import log is created
- **THEN** import log SHALL have status="failed"
- **AND** import log SHALL have `error_message` with validation details
- **AND** import log SHALL have records_imported=0

#### Scenario: Detect re-import of same PDF
- **GIVEN** import log with file_hash="xyz789..." exists
- **WHEN** same PDF is imported again (same file_hash)
- **THEN** system SHALL detect duplicate via `ImportLogRepository.get_by_file_hash()`
- **AND** user SHALL be warned about re-import

### Requirement: Alembic Migrations for Schema Versioning
The system SHALL use Alembic to manage database schema changes with version control.

#### Scenario: Initial migration creation
- **GIVEN** SQLAlchemy models defined in `database/models.py`
- **WHEN** `alembic revision --autogenerate -m "initial schema"` executes
- **THEN** migration file SHALL be created in `database/migrations/versions/`
- **AND** migration SHALL include CREATE TABLE statements for all four tables
- **AND** migration SHALL include CREATE INDEX statements
- **AND** migration SHALL include foreign key and check constraints

#### Scenario: Migration application
- **GIVEN** a migration file in `database/migrations/versions/`
- **WHEN** `alembic upgrade head` executes
- **THEN** all migrations SHALL be applied to database
- **AND** `alembic_version` table SHALL track current migration version
- **AND** database schema SHALL match SQLAlchemy models

#### Scenario: Migration rollback
- **GIVEN** a database with applied migrations
- **WHEN** `alembic downgrade -1` executes
- **THEN** most recent migration SHALL be rolled back
- **AND** database schema SHALL revert to previous version
- **AND** data SHALL be preserved if migration is reversible

### Requirement: Repository Pattern for Data Access
The system SHALL implement repository classes to encapsulate all database operations using SQLAlchemy ORM.

#### Scenario: Account repository CRUD operations
- **GIVEN** `AccountRepository` instance
- **WHEN** `create()`, `get_by_id()`, `get_by_name()`, `list_all()` methods are called
- **THEN** all operations SHALL use SQLAlchemy ORM (no raw SQL)
- **AND** all operations SHALL use database sessions correctly
- **AND** all operations SHALL handle exceptions appropriately

#### Scenario: Transaction repository bulk insert
- **GIVEN** 1000 transactions to insert
- **WHEN** `TransactionRepository.bulk_create()` executes
- **THEN** transactions SHALL be inserted in batches of 1000 (SQLAlchemy bulk operations)
- **AND** bulk insert SHALL be atomic (all or nothing)
- **AND** bulk insert SHALL complete in < 1 second

#### Scenario: Transaction deduplication check
- **GIVEN** a transaction hash
- **WHEN** `TransactionRepository.get_by_hash(hash)` executes
- **THEN** repository SHALL query database for existing transaction with same hash
- **AND** if found, SHALL return existing transaction
- **AND** if not found, SHALL return None

### Requirement: Database Connection Management
The system SHALL manage PostgreSQL database connections via SQLAlchemy sessions.

#### Scenario: Database connection configuration
- **GIVEN** environment variable `DATABASE_URL=postgresql://finance_user:password@localhost:5432/finance_db`
- **WHEN** database connection is initialized
- **THEN** SQLAlchemy engine SHALL be created with connection URL
- **AND** connection pool SHALL be configured (pool_size=5, max_overflow=10)
- **AND** connection SHALL use psycopg2 driver

#### Scenario: Session lifecycle management
- **GIVEN** a database operation
- **WHEN** repository method executes
- **THEN** session SHALL be created from session factory
- **AND** session SHALL be committed on success
- **AND** session SHALL be rolled back on exception
- **AND** session SHALL be closed after operation

### Requirement: Financial Data Precision
The system SHALL use NUMERIC type for all financial amounts to prevent float rounding errors.

#### Scenario: Decimal precision preservation
- **GIVEN** transaction amount 123.45
- **WHEN** amount is stored in database
- **THEN** amount SHALL be stored as NUMERIC(12,2)
- **AND** amount SHALL be retrieved as Decimal("123.45") (not float)
- **AND** no rounding errors SHALL occur in calculations

#### Scenario: Large amount support
- **GIVEN** transaction amount 9,999,999,999.99 (10 digits + 2 decimals)
- **WHEN** amount is stored in database
- **THEN** amount SHALL fit in NUMERIC(12,2) column
- **AND** amount SHALL be stored without truncation
