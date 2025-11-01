# Project Context

## Purpose
Build a simplified personal finance tracking system that converts bank statement PDFs into structured data for visualization and analysis. The system will:
- Extract transaction data from PDF bank statements using Docling
- Convert PDFs to CSV format for processing
- Store financial transactions in a local PostgreSQL database
- Visualize financial data through Grafana dashboards
- Run entirely in containerized Docker environment for easy deployment

Primary goal: Create a self-hosted, privacy-focused alternative to cloud-based finance apps, processing locally stored bank statements without external API dependencies.

## Tech Stack
- **Language**: Python 3.11+
- **Database**: PostgreSQL 18 (local instance)
- **PDF Processing**: Docling (PDF to CSV conversion)
- **Data Processing**: pandas, NumPy
- **Database ORM**: SQLAlchemy with psycopg2
- **Visualization**: Grafana (dashboards and analytics)
- **Containerization**: Docker & Docker Compose
- **Configuration**: python-dotenv for environment variables
- **Testing**: pytest, pytest-cov

## Project Conventions

### Code Style
- Follow PEP 8 style guide strictly
- Use Black formatter (line length: 88)
- Type hints required for all function signatures (enforce with mypy)
- Docstrings for all public functions (Google style)
- Use meaningful variable names: `transaction_date`, `account_balance`, `csv_parser`
- Imports organized: stdlib → third-party → local (isort)
- Maximum function complexity: 10 (enforce with flake8)

### Architecture Patterns
- **ETL Pipeline Architecture**: Extract (PDF) → Transform (CSV parsing) → Load (PostgreSQL)
- **Separation of Concerns**:
  - `pdf_processor/` - Docling PDF extraction
  - `csv_parser/` - CSV parsing and validation
  - `database/` - SQLAlchemy models and repository pattern
  - `ingestion/` - Orchestration and business logic
- **Database Schema**: Normalized tables (`accounts`, `transactions`, `categories`, `import_logs`)
- **Idempotent Operations**: Hash-based deduplication for transactions
- **Repository Pattern**: Abstract database operations behind repositories
- **Dependency Injection**: Pass dependencies explicitly, avoid global state
- **Batch Processing**: Process statements in configurable batch sizes

#### Database Access Strategy
**Decision: Use SQLAlchemy ORM exclusively - NO raw SQL queries**

**Rationale:**
1. **Type Safety**: SQLAlchemy models provide Python type checking and Pydantic integration, critical for financial data where decimal precision matters (avoiding float rounding errors)
2. **Maintainability**: Schema changes are version-controlled via Alembic migrations, making database evolution traceable and reversible
3. **Testability**: Repository pattern with ORM allows easy mocking for unit tests and in-memory SQLite for fast test execution without spinning up PostgreSQL
4. **Project Scope Alignment**: Personal finance app with simple CRUD operations (100-1000 transactions/month) doesn't require raw SQL performance optimizations
5. **Architecture Consistency**: Repository Pattern abstracts data access - business logic never sees SQL, maintaining clean separation of concerns
6. **Developer Experience**: Models serve as living documentation, IDE autocomplete works, refactoring is safe

**Implementation Rules:**
- All database interactions MUST use SQLAlchemy ORM (no raw SQL or `session.execute()` with text queries)
- Use Alembic for ALL schema changes (never manual ALTER TABLE statements)
- Repository classes encapsulate all database operations using SQLAlchemy query API
- Financial amounts MUST use `NUMERIC`/`Decimal` types (never float)
- Exception: Database views for complex Grafana analytics may be created via Alembic migrations if ORM-generated queries become inefficient

**Trade-offs Accepted:**
- Slightly lower raw performance vs hand-tuned SQL (acceptable for personal use scale)
- Learning curve for SQLAlchemy query API (outweighed by long-term maintainability)
- ORM abstraction may hide database behavior (mitigated by SQL query logging in development)

### Testing Strategy
- **Unit Tests**: All parsing logic, data transformations, and business rules
- **Integration Tests**: Database operations with test PostgreSQL container
- **Fixture-Based Testing**: Sample bank PDFs from multiple institutions
- **Test Coverage**: Minimum 80% coverage requirement (pytest-cov)
- **Mock External Dependencies**: File system operations, database in unit tests
- **Data Validation Tests**: Schema validation, data type checks, constraint verification
- **Test Data**: Anonymized real-world bank statement samples
- **CI/CD**: All tests must pass before merge

### Git Workflow
- **Branching Strategy**: 
  - `main` - Production-ready code only
  - `develop` - Integration branch
  - `feature/*` - New features
  - `fix/*` - Bug fixes
  - `docs/*` - Documentation updates
- **Commit Convention**: Conventional Commits
  - `feature:` - New features
  - `fix:` - Bug fixes
  - `docs:` - Documentation
  - `refactor:` - Code refactoring
  - `test:` - Test additions/changes
  - `chore:` - Maintenance tasks
- **PR Requirements**: 
  - All tests passing
  - Docker build succeeds
  - Code review approved
  - No decrease in test coverage
- **Release Management**: Semantic versioning (v1.0.0, v1.1.0, v2.0.0)

## Domain Context

### Banking Domain Knowledge
- **Bank Statements**: PDFs contain: transaction date, posting date, description, debit/credit amounts, running balance
- **Transaction Types**: 
  - Income (deposits, transfers in, interest)
  - Expenses (withdrawals, purchases, fees)
  - Transfers (between accounts)
- **Account Types**: Checking, savings, credit card, loan accounts
- **Statement Formats**: Each bank has unique PDF layouts (Chase, Bank of America, Wells Fargo, etc.)
- **Data Challenges**: 
  - Inconsistent date formats
  - Multi-line descriptions
  - Currency symbols and formatting
  - Split transactions
  - Pending vs posted transactions

### Financial Data Characteristics
- **Time Series Nature**: All data is date-indexed and chronological
- **Double-Entry Bookkeeping**: Every transaction affects at least one account
- **Currency Handling**: Support USD primarily, extensible to multi-currency
- **Precision Requirements**: Financial amounts require decimal precision (avoid floats)
- **Historical Data**: Immutable once imported (no editing historical transactions)
- **Categorization**: Transactions should be categorizable (groceries, utilities, etc.)

## Important Constraints

### Privacy & Security
- **Privacy First**: No data leaves local environment - zero external APIs
- **Local Only**: Must run on single machine without internet dependency
- **No Cloud Services**: No Plaid, no external aggregators, no telemetry
- **Data Ownership**: User owns all data, stored locally in PostgreSQL

### Technical Constraints
- **Docker Required**: Entire stack must be deployable via `docker-compose up`
- **Read-Only Source Files**: Never modify original PDF statements
- **Idempotent Imports**: Re-importing same statement shouldn't duplicate transactions
- **Database Migrations**: Schema changes must support forward migrations (Alembic)
- **Resource Limits**: Designed for personal use (100-1000 transactions/month)
- **File Size Limits**: Support PDFs up to 50MB
- **Python Version**: Minimum Python 3.11

### Operational Constraints
- **Single User**: No multi-user authentication required
- **Manual Upload**: User manually places PDFs in watched directory (local filesystem)
- **Batch Processing**: Process statements on schedule or manual trigger
- **Error Recovery**: Failed imports should not corrupt database
- **Logging**: Comprehensive logging for debugging import issues

## External Dependencies

### Core Dependencies
- **Docling**: PDF extraction and document processing
- **uv**: Fast Python package installer and resolver (by Astral)
- **PostgreSQL**: Relational database (official Docker image: postgres:18-alpine)
- **Grafana**: Visualization and dashboards (official Docker image: grafana/grafana:latest)

### Python Libraries
- **Data Processing**: pandas, NumPy
- **Database**: SQLAlchemy, psycopg2-binary, alembic
- **Configuration**: python-dotenv, pydantic (settings validation)
- **Testing**: pytest, pytest-cov, pytest-docker
- **Utilities**: python-dateutil (date parsing), click (CLI)
- **Logging**: structlog (structured logging)

### Infrastructure
- **Docker Engine**: Container runtime (Docker Desktop or Docker CE 20+)
- **Docker Compose**: Multi-container orchestration (v2.0+)
- **File System**: Local directory structure for PDF storage and CSV staging
  - `/data/pdfs/` - Input PDF statements
  - `/data/csv/` - Intermediate CSV files
  - `/data/processed/` - Successfully processed files
  - `/data/failed/` - Failed imports for manual review

### Optional Dependencies
- **Monitoring**: Prometheus (if Grafana metrics needed)
- **Scheduler**: APScheduler (for automated processing)