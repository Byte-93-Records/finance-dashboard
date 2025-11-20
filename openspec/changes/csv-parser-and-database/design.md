# Design: CSV Parser and Database Schema

## Context

The finance dashboard ETL pipeline has completed the **Extract** phase (PDF → CSV using Docling). This design addresses the **Transform** and **Load** phases to complete the ETL pipeline:

- **Transform Phase**: Parse and validate CSV files from PDF extraction, ensuring data quality before database ingestion
- **Load Phase**: Define PostgreSQL database schema and implement data loading with deduplication

**Current State:**
- PDFs successfully extracted to CSV format in `/data/csv/`
- CSV schema standardized with required columns: `transaction_date`, `description`, `amount`, `transaction_type`
- Original PDFs moved to `/data/processed/` or `/data/failed/`

**Constraints:**
- **Data Integrity**: No silent failures or data corruption (financial data correctness critical)
- **Deduplication**: Prevent duplicate transactions from re-importing same PDF
- **Schema Evolution**: Support database migrations via Alembic
- **Privacy-First**: All data stored locally in PostgreSQL (no external APIs)
- **Python 3.11+**: Minimum version requirement
- **Repository Pattern**: All database access via repositories (per project conventions)
- **SQLAlchemy ORM Only**: No raw SQL queries (per project database access strategy)

**Stakeholders:**
- **End User**: Expects reliable data loading with clear error messages for failed imports
- **Downstream Systems**: Grafana dashboards depend on clean, normalized transaction data
- **Database**: PostgreSQL 18 running in Docker

## Goals / Non-Goals

**Goals:**
1. Parse CSV files from PDF extraction into validated Pydantic models
2. Define normalized PostgreSQL schema for financial transactions
3. Implement hash-based deduplication to prevent duplicate transactions
4. Provide clear, actionable error messages for validation failures
5. Support schema migrations with Alembic for future evolution
6. Enable comprehensive testing with fixture CSVs and test database

**Non-Goals:**
- Real-time data ingestion (batch processing sufficient for personal use)
- Multi-user support (single-user application for v1)
- Advanced categorization (basic category support, ML categorization deferred)
- Data export features (focus on ingestion only)
- Web API (Grafana queries PostgreSQL directly)
- OCR or scanned PDF support (text-based PDFs only)

## Decisions

### Decision 1: Pydantic for CSV Parsing and Validation
**Choice:** Use Pydantic models for CSV row validation

**Rationale:**
- **Type Safety**: Automatic validation with Python type hints (date parsing, decimal precision)
- **Financial Precision**: Pydantic's `Decimal` type prevents float rounding errors critical for money
- **Error Messages**: Clear validation errors with field names and expected types
- **SQLAlchemy Integration**: Pydantic models easily convert to SQLAlchemy models

**Alternatives Considered:**
1. **pandas** - Overkill for simple CSV parsing, heavy dependency, less precise error messages
2. **csv.DictReader + manual validation** - Too much boilerplate, error-prone, no type safety
3. **marshmallow** - Good validation but Pydantic has better type hints and performance

**Why Pydantic Wins:** Best balance of type safety, validation quality, and developer experience. Aligns with project's type hint requirements (mypy enforcement).

**Implementation:**
```python
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date

class TransactionRow(BaseModel):
    transaction_date: date
    posting_date: date | None = None
    description: str = Field(min_length=1)
    amount: Decimal = Field(decimal_places=2)
    balance: Decimal | None = Field(decimal_places=2, default=None)
    transaction_type: str = Field(pattern="^(debit|credit)$")
```

### Decision 2: Hash-Based Transaction Deduplication
**Choice:** Generate SHA-256 hash from `(account_id, transaction_date, amount, description_normalized)`

**Rationale:**
- **Idempotent Imports**: Re-importing same PDF doesn't create duplicates (project constraint)
- **Deterministic**: Same transaction always produces same hash
- **Database Enforcement**: Unique constraint on `transaction_hash` column prevents duplicates at DB level
- **No Import Tracking**: Don't need to track which PDF each transaction came from (simpler)

**Hash Components:**
- `account_id` - Prevents cross-account collisions (same transaction on different accounts)
- `transaction_date` - When transaction occurred (not posting_date, which may vary)
- `amount` - Transaction amount including sign (negative for expenses)
- `description_normalized` - Lowercased, whitespace-stripped description

**Normalization Rules:**
```python
def normalize_description(desc: str) -> str:
    return desc.strip().lower()  # Conservative: only lowercase + strip whitespace
```

**Edge Cases:**
- **Legitimate Duplicates**: Two identical transactions same day (e.g., two $5 coffees) will be deduplicated
  - **Mitigation**: Log deduplicated transactions for user review, document limitation in user guide
- **Description Variations**: "STARBUCKS #1234" vs "STARBUCKS #5678" will be treated as different
  - **Acceptable**: Conservative normalization prevents false positives

### Decision 3: Normalized Database Schema
**Choice:** Four-table normalized schema: `accounts`, `transactions`, `categories`, `import_logs`

**Schema Design:**
```sql
-- Account information (manually created by user)
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,                    -- "Chase Checking", "Amex Blue Cash"
    account_type VARCHAR(50) NOT NULL,             -- checking, savings, credit_card, brokerage
    institution VARCHAR(255),                      -- "Chase Bank", "American Express"
    created_at TIMESTAMP DEFAULT NOW()
);

-- Financial transactions (imported from CSVs)
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    transaction_date DATE NOT NULL,
    posting_date DATE,
    description TEXT NOT NULL,
    amount NUMERIC(12,2) NOT NULL,                 -- NUMERIC for financial precision
    balance NUMERIC(12,2),
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('debit', 'credit')),
    transaction_hash VARCHAR(64) UNIQUE NOT NULL,  -- SHA-256 hash for deduplication
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_account_date ON transactions(account_id, transaction_date);

-- Transaction categories (optional for v1, manually assigned)
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,             -- "Groceries", "Utilities", "Dining"
    parent_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,  -- Future: category hierarchy
    created_at TIMESTAMP DEFAULT NOW()
);

-- Import history tracking (which PDFs were processed)
CREATE TABLE import_logs (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,                -- Original PDF filename
    file_hash VARCHAR(64) NOT NULL,                -- SHA-256 of PDF file (detect re-imports)
    import_date TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'failed', 'partial')),
    records_imported INTEGER,                      -- Number of transactions imported
    records_skipped INTEGER,                       -- Number of duplicates skipped
    error_message TEXT
);
```

**Rationale:**
- **Normalization**: Reduces data redundancy (account info not repeated per transaction)
- **Referential Integrity**: Foreign keys prevent orphaned transactions
- **Indexes**: Optimize common queries (transactions by date, by account+date for Grafana)
- **NUMERIC Type**: Prevents float rounding errors (per project database strategy)
- **Unique Constraint**: `transaction_hash` enforces deduplication at database level
- **Import Logs**: Track PDF processing history for debugging and audit trail

**Design Choices:**
- **No `user_id`**: Single-user application (per project constraints)
- **Optional `category_id`**: Categories can be assigned later, not required for import
- **`parent_id` in categories**: Supports future category hierarchy (e.g., "Dining" → "Fast Food")
- **`file_hash` in import_logs**: Detect when same PDF is re-imported

### Decision 4: Repository Pattern for Data Access
**Choice:** Implement repository classes for all database operations (per project architecture)

**Repository Interfaces:**
```python
class AccountRepository:
    def create(self, account: Account) -> Account
    def get_by_id(self, id: int) -> Account | None
    def get_by_name(self, name: str) -> Account | None
    def list_all(self) -> list[Account]

class TransactionRepository:
    def create(self, transaction: Transaction) -> Transaction
    def bulk_create(self, transactions: list[Transaction]) -> int  # Returns count inserted
    def get_by_hash(self, hash: str) -> Transaction | None
    def list_by_account(self, account_id: int, start_date: date, end_date: date) -> list[Transaction]
    def count_by_account(self, account_id: int) -> int

class ImportLogRepository:
    def create(self, log: ImportLog) -> ImportLog
    def get_by_file_hash(self, file_hash: str) -> ImportLog | None
```

**Rationale:**
- **Testability**: Mock repositories in unit tests without database (per project testing strategy)
- **Abstraction**: Business logic doesn't know about SQLAlchemy (clean separation)
- **Query Reusability**: Common queries centralized (e.g., "find duplicate transactions")
- **Migration Safety**: Schema changes only affect repositories, not business logic

**Alignment with Project Conventions:**
- Per `project.md` Repository Pattern Strategy: "Repositories handle data access, services handle business rules"
- Per `project.md` Database Access Strategy: "Repository classes encapsulate all database operations using SQLAlchemy query API"

### Decision 5: Alembic for Schema Migrations
**Choice:** Use Alembic for database schema versioning (per project database strategy)

**Rationale:**
- **Version Control**: Schema changes tracked in Git via migration files
- **Rollback Support**: Failed migrations can be reverted with `alembic downgrade`
- **Auto-Generation**: `alembic revision --autogenerate` generates migrations from SQLAlchemy model changes
- **Project Standard**: Aligns with project database access strategy ("Use Alembic for ALL schema changes")

**Migration Workflow:**
1. Modify SQLAlchemy models in `database/models.py`
2. Generate migration: `alembic revision --autogenerate -m "add transactions table"`
3. Review generated SQL in `database/migrations/versions/xxx_add_transactions_table.py`
4. Apply migration: `alembic upgrade head`
5. Verify in PostgreSQL: `\dt` to list tables

**Initial Migration:**
- Create all four tables: `accounts`, `transactions`, `categories`, `import_logs`
- Add indexes: `idx_transactions_date`, `idx_transactions_account_date`
- Add constraints: unique `transaction_hash`, foreign keys, check constraints

### Decision 6: Fail-Fast CSV Validation (No Auto-Correction)
**Choice:** Reject invalid CSVs with detailed error messages, no automatic data correction

**Approach:**
- **Pydantic Validation**: Collect all validation errors per row
- **Detailed Logging**: Log row number, field name, expected type, actual value
- **No Auto-Correction**: Never guess dates, fix amounts, or infer missing fields
- **User Action Required**: User must fix source PDF or manually correct CSV

**Example Error Message:**
```
CSV Validation Failed: /data/csv/chase_statement_2024-01.csv
Row 5: transaction_date - invalid date format "01/15/2024" (expected YYYY-MM-DD)
Row 12: amount - invalid decimal "1,234.56" (remove commas)
Row 18: transaction_type - invalid value "purchase" (expected debit or credit)
```

**Rationale:**
- **Financial Correctness**: Auto-correction risks data integrity (wrong amounts catastrophic)
- **User Trust**: Explicit errors better than silent corrections
- **Debugging**: Clear errors help user fix source PDFs or Docling configuration

## Implementation Architecture

### Module Structure
```
csv_parser/
├── __init__.py
├── parser.py           # CSVParser class (Pydantic validation)
├── models.py           # Pydantic models (TransactionRow)
├── hasher.py           # TransactionHasher (SHA-256 for deduplication)
└── exceptions.py       # ValidationError, ParsingError

database/
├── __init__.py
├── models.py           # SQLAlchemy ORM models (Account, Transaction, Category, ImportLog)
├── repositories.py     # Repository implementations (AccountRepository, TransactionRepository)
├── connection.py       # Database session management
└── migrations/         # Alembic migrations
    ├── env.py
    ├── script.py.mako
    └── versions/
```

### Core Classes

**CSVParser** (`csv_parser/parser.py`):
- **Responsibility**: Parse CSV files into validated Pydantic models
- **Methods**: `parse(csv_path: Path) -> list[TransactionRow]`
- **Error Handling**: Raises `ValidationError` with row-level details
- **Validation**: Uses Pydantic models for type checking, date parsing, decimal precision

**TransactionHasher** (`csv_parser/hasher.py`):
- **Responsibility**: Generate deterministic SHA-256 hashes for transaction deduplication
- **Methods**: `hash_transaction(account_id: int, date: date, amount: Decimal, description: str) -> str`
- **Normalization**: Lowercase description, strip whitespace before hashing
- **Usage**: Used by database loading to check for duplicate transactions

**AccountRepository / TransactionRepository** (`database/repositories.py`):
- **Responsibility**: Database CRUD operations via SQLAlchemy ORM
- **Methods**: Standard create, read, update, delete operations
- **Transaction Support**: Use SQLAlchemy sessions for atomic operations

### Processing Flow
```
1. CSV files available in /data/csv/ (from PDF extraction)
2. For each CSV:
   a. Parse CSV with CSVParser (Pydantic validation)
   b. Normalize descriptions with TransactionHasher
   c. Generate transaction hashes
   d. Check for existing hashes via TransactionRepository.get_by_hash()
   e. Bulk insert new transactions via TransactionRepository.bulk_create()
   f. Create import log via ImportLogRepository.create()
3. CSV processing complete (orchestration handled by separate ingestion module)
```

## Risks / Trade-offs

### Risk 1: Hash Collision for Legitimate Duplicates
**Risk:** Two legitimate transactions on same day with same amount and description will be deduplicated (e.g., two $5 Starbucks purchases same day)

**Mitigation:**
- Document limitation in user guide
- Log deduplicated transactions with details for user review
- Future enhancement: Manual override to force import duplicate
- Consider adding bank transaction ID to hash if available in statements

**Likelihood:** Medium (common for small recurring purchases)  
**Impact:** Low (user can manually add missing transaction if noticed)

### Risk 2: Database Migration Failures
**Risk:** Alembic migrations may fail on production database (e.g., constraint violations, data type mismatches)

**Mitigation:**
- Test migrations on copy of production database first
- Backup database before migrations: `pg_dump finance > backup.sql`
- Use Alembic's `--sql` flag to review SQL before execution
- Implement rollback procedures: `alembic downgrade -1`
- Add migration tests in CI/CD

**Likelihood:** Low (simple schema, no complex data transformations)  
**Impact:** High (database corruption would lose all data)

### Risk 3: CSV Parsing Performance for Large Files
**Risk:** Large CSV files (10,000+ transactions) may cause memory issues or slow parsing

**Mitigation:**
- Stream CSV parsing (process row-by-row, don't load entire file into memory)
- Bulk insert in batches of 1000 transactions (SQLAlchemy bulk operations)
- Monitor memory usage during testing with large fixtures
- Set CSV size limits: warn if > 50MB, reject if > 100MB
- Use Python generators for memory-efficient processing

**Likelihood:** Low (personal finance rarely has 10,000+ transactions per statement)  
**Impact:** Medium (slow imports acceptable, crashes not acceptable)

### Risk 4: Description Normalization Accuracy
**Risk:** Over-normalization may cause false duplicates (e.g., "STARBUCKS #1234" and "STARBUCKS #5678" treated as same), under-normalization may miss duplicates

**Mitigation:**
- Conservative normalization: only lowercase + whitespace stripping (no removing numbers/special chars)
- Test with real transaction data from multiple banks (Chase, Amex, Fidelity)
- Provide configuration for normalization rules (future enhancement)
- Log normalized descriptions for debugging: `logger.debug(f"Normalized: {original} -> {normalized}")`

**Likelihood:** Medium (bank descriptions vary widely)  
**Impact:** Low (false negatives better than false positives for financial data)

### Trade-off 1: No Automatic Categorization
**Accepted:** Categories must be manually assigned (v1)

**Justification:**
- ML-based categorization adds significant complexity (training data, model maintenance)
- Manual categorization acceptable for personal finance (100-1000 transactions/month)
- Can be added in future enhancement (v2)
- Focus on core ETL pipeline first (Extract, Transform, Load)

### Trade-off 2: Single-User Design
**Accepted:** No multi-user support, no authentication, no user_id columns

**Justification:**
- Personal finance dashboard (single user per project constraints)
- Simplifies database schema (no user_id foreign keys)
- Simplifies application logic (no permission checks)
- Can be added later if needed (add user_id columns via migration)

### Trade-off 3: Manual Account Creation
**Accepted:** Accounts must be manually created before importing transactions (no auto-creation from CSV metadata)

**Justification:**
- Prevents accidental account creation from malformed CSVs
- User explicitly defines account names and types
- Simpler error handling (reject CSV if account doesn't exist)
- Future enhancement: Auto-create accounts with user confirmation

## Migration Plan

**Initial Setup:**
1. Create module directories: `csv_parser/`, `database/`
2. Add dependencies to `pyproject.toml`:
   - SQLAlchemy >= 2.0
   - Alembic >= 1.13
   - Pydantic >= 2.0
   - psycopg2-binary >= 2.9
3. Initialize Alembic: `alembic init database/migrations`
4. Configure database connection in `.env`:
   ```
   DATABASE_URL=postgresql://finance_user:password@localhost:5432/finance_db
   ```
5. Add PostgreSQL service to `docker-compose.yml` (postgres:18-alpine)

**Database Setup:**
1. Create SQLAlchemy models in `database/models.py`
2. Generate initial migration: `alembic revision --autogenerate -m "initial schema"`
3. Review migration file in `database/migrations/versions/`
4. Apply migration: `alembic upgrade head`
5. Verify tables: `docker-compose exec postgres psql -U finance_user -d finance_db -c "\dt"`

**Testing Approach:**
1. Create test fixtures: Sample CSVs with valid/invalid data (10+ scenarios)
2. Unit tests:
   - CSV parser validation (valid dates, invalid amounts, missing fields)
   - Hash generation (deterministic, normalization)
   - Repositories (CRUD operations, deduplication)
3. Integration tests:
   - End-to-end CSV → database flow with test PostgreSQL container
   - Test deduplication: Import same CSV twice, verify no duplicates
   - Test rollback: Validation failure mid-import, verify no partial data
4. Fixture-based tests: Real anonymized bank statement CSVs (Chase, Amex, Fidelity)

**Rollback Plan:**
- Database rollback: `alembic downgrade base` (removes all tables)
- Drop database: `docker-compose down -v` (removes PostgreSQL volume)
- Remove modules: Delete `csv_parser/`, `database/`
- Revert dependencies: Remove SQLAlchemy, Alembic, Pydantic from `pyproject.toml`
- No data loss risk: PDFs preserved in `/data/processed/`, CSVs can be regenerated

## Open Questions

1. **Account Creation Workflow**: Should accounts be auto-created from CSV metadata (institution name, account type) or manually created first?
   - **Recommendation**: Manual creation first (v1), auto-creation with confirmation (v2)

2. **Category Hierarchy Depth**: How deep should category nesting go? (e.g., "Dining" → "Fast Food" → "Burgers")
   - **Recommendation**: Single-level for v1 (no nesting), add `parent_id` support for v2

3. **Transaction Editing**: Should users be able to edit imported transactions (amount, description, date)?
   - **Recommendation**: Read-only for v1 (data integrity), add edit capability with audit trail (v2)

4. **Import History Tracking**: Should we track which specific transactions came from which PDF?
   - **Recommendation**: Yes, add `import_log_id` foreign key to `transactions` table

5. **Timezone Handling**: Should transaction dates include timezone information?
   - **Recommendation**: No, use `DATE` type (not `TIMESTAMP`), assume local timezone (per project constraints)
