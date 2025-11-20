# Tasks: CSV Parser and Database Schema

## 1. Project Setup
- [ ] 1.1 Create module directories: `csv_parser/`, `database/`
- [ ] 1.2 Add dependencies to `pyproject.toml`:
  - [ ] 1.2.1 SQLAlchemy >= 2.0
  - [ ] 1.2.2 Alembic >= 1.13
  - [ ] 1.2.3 Pydantic >= 2.0
  - [ ] 1.2.4 psycopg2-binary >= 2.9
- [ ] 1.3 Initialize Alembic: `alembic init database/migrations`
- [ ] 1.4 Configure database connection in `.env`:
  - [ ] 1.4.1 Add `DATABASE_URL=postgresql://finance_user:password@localhost:5432/finance_db`
- [ ] 1.5 Add PostgreSQL service to `docker-compose.yml` (postgres:18-alpine)
- [ ] 1.6 Configure volume mounts for PostgreSQL data persistence

## 2. Database Schema Implementation
- [ ] 2.1 Create SQLAlchemy models in `database/models.py`:
  - [ ] 2.1.1 `Account` model (id, name, account_type, institution, created_at)
  - [ ] 2.1.2 `Transaction` model (id, account_id, transaction_date, posting_date, description, amount, balance, transaction_type, transaction_hash, category_id, created_at)
  - [ ] 2.1.3 `Category` model (id, name, parent_id, created_at)
  - [ ] 2.1.4 `ImportLog` model (id, filename, file_hash, import_date, status, records_imported, records_skipped, error_message)
- [ ] 2.2 Add foreign key relationships and constraints
- [ ] 2.3 Add indexes: `idx_transactions_date`, `idx_transactions_account_date`
- [ ] 2.4 Generate initial Alembic migration: `alembic revision --autogenerate -m "initial schema"`
- [ ] 2.5 Review generated migration file
- [ ] 2.6 Apply migration: `alembic upgrade head`
- [ ] 2.7 Verify tables created: `docker-compose exec postgres psql -U finance_user -d finance_db -c "\dt"`

## 3. Repository Pattern Implementation
- [ ] 3.1 Create `database/connection.py` for session management
- [ ] 3.2 Implement `AccountRepository` in `database/repositories.py`:
  - [ ] 3.2.1 `create(account: Account) -> Account`
  - [ ] 3.2.2 `get_by_id(id: int) -> Account | None`
  - [ ] 3.2.3 `get_by_name(name: str) -> Account | None`
  - [ ] 3.2.4 `list_all() -> list[Account]`
- [ ] 3.3 Implement `TransactionRepository` in `database/repositories.py`:
  - [ ] 3.3.1 `create(transaction: Transaction) -> Transaction`
  - [ ] 3.3.2 `bulk_create(transactions: list[Transaction]) -> int`
  - [ ] 3.3.3 `get_by_hash(hash: str) -> Transaction | None`
  - [ ] 3.3.4 `list_by_account(account_id: int, start_date: date, end_date: date) -> list[Transaction]`
  - [ ] 3.3.5 `count_by_account(account_id: int) -> int`
- [ ] 3.4 Implement `ImportLogRepository` in `database/repositories.py`:
  - [ ] 3.4.1 `create(log: ImportLog) -> ImportLog`
  - [ ] 3.4.2 `get_by_file_hash(file_hash: str) -> ImportLog | None`

## 4. CSV Parser Implementation
- [ ] 4.1 Create Pydantic models in `csv_parser/models.py`:
  - [ ] 4.1.1 `TransactionRow` model with validation (transaction_date, posting_date, description, amount, balance, transaction_type)
  - [ ] 4.1.2 Add field validators (date format YYYY-MM-DD, decimal precision, transaction_type enum)
- [ ] 4.2 Implement `CSVParser` class in `csv_parser/parser.py`:
  - [ ] 4.2.1 `parse(csv_path: Path) -> list[TransactionRow]`
  - [ ] 4.2.2 Stream CSV parsing (row-by-row, not load entire file)
  - [ ] 4.2.3 Collect validation errors per row
  - [ ] 4.2.4 Raise `ValidationError` with detailed row-level errors
- [ ] 4.3 Create custom exceptions in `csv_parser/exceptions.py`:
  - [ ] 4.3.1 `ValidationError` (with row number, field name, error message)
  - [ ] 4.3.2 `ParsingError` (for CSV format issues)

## 5. Transaction Hashing
- [ ] 5.1 Implement `TransactionHasher` in `csv_parser/hasher.py`:
  - [ ] 5.1.1 `hash_transaction(account_id: int, date: date, amount: Decimal, description: str) -> str`
  - [ ] 5.1.2 SHA-256 hash generation
  - [ ] 5.1.3 Description normalization (lowercase, strip whitespace)
- [ ] 5.2 Add unit tests for TransactionHasher (deterministic hashing, normalization)

## 6. Testing
- [ ] 6.1 Create test fixtures in `tests/fixtures/`:
  - [ ] 6.1.1 Valid CSV samples (10+ rows)
  - [ ] 6.1.2 Invalid CSV samples (missing columns, bad dates, invalid amounts)
  - [ ] 6.1.3 Duplicate transaction scenarios
  - [ ] 6.1.4 Anonymized real bank statement CSVs (Chase, Amex, Fidelity)
- [ ] 6.2 Unit tests for CSV parser:
  - [ ] 6.2.1 Valid date parsing (YYYY-MM-DD)
  - [ ] 6.2.2 Invalid date formats (MM/DD/YYYY, DD/MM/YYYY)
  - [ ] 6.2.3 Decimal precision validation (2 decimal places)
  - [ ] 6.2.4 Transaction type validation (debit/credit only)
  - [ ] 6.2.5 Missing required fields
- [ ] 6.3 Unit tests for transaction hasher:
  - [ ] 6.3.1 Deterministic hash generation (same input = same hash)
  - [ ] 6.3.2 Description normalization (lowercase, whitespace stripping)
  - [ ] 6.3.3 Different accounts produce different hashes
- [ ] 6.4 Unit tests for repositories (with test database):
  - [ ] 6.4.1 Account CRUD operations
  - [ ] 6.4.2 Transaction bulk insert
  - [ ] 6.4.3 Deduplication (get_by_hash)
  - [ ] 6.4.4 Query by account and date range
- [ ] 6.5 Integration tests:
  - [ ] 6.5.1 CSV parsing → database loading flow
  - [ ] 6.5.2 Import same CSV twice (verify no duplicates)
  - [ ] 6.5.3 Validation failure (verify rollback, no partial data)
  - [ ] 6.5.4 Large CSV handling (1000+ rows)
- [ ] 6.6 Verify 80% test coverage requirement (pytest-cov)

## 7. Documentation
- [ ] 7.1 Document CSV schema in `docs/csv_schema.md`
- [ ] 7.2 Document database schema in `docs/database_schema.md`
- [ ] 7.3 Document deduplication behavior and limitations
- [ ] 7.4 Add troubleshooting guide for common errors

## 8. Code Quality
- [ ] 8.1 Add type hints to all functions (mypy compliance)
- [ ] 8.2 Add docstrings to all public functions (Google style)
- [ ] 8.3 Run Black formatter (line length: 88)
- [ ] 8.4 Run isort for import organization
- [ ] 8.5 Run flake8 linter (max complexity: 10)
- [ ] 8.6 Verify PEP 8 compliance

## 9. Docker Integration
- [ ] 9.1 Test PostgreSQL service starts correctly
- [ ] 9.2 Test database volume persistence (data survives container restart)
- [ ] 9.3 Test Alembic migrations in Docker environment
- [ ] 9.4 Add health check for PostgreSQL service

## 10. Validation & Deployment
- [ ] 10.1 Run full test suite (all tests pass)
- [ ] 10.2 Test with real financial statement CSVs (3+ banks, 2+ credit cards)
- [ ] 10.3 Verify deduplication works correctly
- [ ] 10.4 Verify validation errors are clear and actionable
- [ ] 10.5 Test database migrations (upgrade and downgrade)
- [ ] 10.6 Run `openspec validate csv-parser-and-database --strict`
- [ ] 10.7 Create PR for review
- [ ] 10.8 Update `CHANGELOG.md` with feature addition
