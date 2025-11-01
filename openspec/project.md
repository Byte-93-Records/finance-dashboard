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

### Strategy & Design Decisions

> **Note**: Each strategy below provides rationale and implementation rules. For detailed analysis including code examples and trade-off discussions, see the design strategy documents linked in the [Additional Resources](#additional-resources) section.

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

#### PDF Processing Strategy
**Decision: Use Docling for PDF extraction instead of PyPDF2, pdfplumber, or Camelot**

**Rationale:**
1. **Modern Architecture**: Docling is specifically designed for structured document extraction with ML-based layout understanding
2. **Bank Statement Complexity**: Bank PDFs have complex layouts with tables, multiple columns, headers/footers - Docling handles these better than regex-based parsers
3. **CSV Output**: Direct PDF-to-CSV conversion aligns with ETL pipeline, avoiding custom parsing logic
4. **Maintenance Burden**: Traditional PDF libraries require bank-specific parsers for each institution - Docling generalizes better
5. **Future-Proofing**: ML-based extraction adapts to layout changes without code modifications

**Implementation Rules:**
- Docling processes all PDF inputs into standardized CSV format
- PDF originals remain untouched (read-only)
- Extraction failures logged for manual review, not auto-corrected
- CSV output validated before database ingestion

**Trade-offs Accepted:**
- Dependency on Docling's extraction accuracy (mitigated by validation layer)
- Heavier dependency than simple PDF libraries (acceptable for functionality gained)
- May require Docling configuration per bank format (still less code than custom parsers)

#### Containerization Strategy
**Decision: Docker Compose for entire stack - no local Python/PostgreSQL installations**

**Rationale:**
1. **Reproducibility**: `docker-compose up` guarantees identical environment across machines
2. **Isolation**: No conflicts with system Python, database versions, or other projects
3. **Dependency Management**: All services (PostgreSQL, Grafana, Python) versioned and orchestrated together
4. **Simplified Setup**: New users don't need to install PostgreSQL, configure ports, manage Python versions
5. **Production Parity**: Development environment matches deployment environment exactly

**Implementation Rules:**
- All services defined in `docker-compose.yml` with explicit version pinning
- Python dependencies managed via `uv` in Docker image for fast builds
- PostgreSQL data persisted via Docker volumes (survives container restarts)
- Environment variables via `.env` file (never hardcoded)
- Health checks ensure services start in correct order

**Trade-offs Accepted:**
- Docker overhead on resource-constrained machines (minimal impact for small dataset)
- Learning curve for Docker debugging (offset by improved reliability)
- Slower iteration vs local Python (mitigated by volume mounts for code hot-reloading)

**See Also**: [Docker vs Podman Analysis](../docs/design_strategies/docker_v_podman_strategy.md) for detailed comparison and why Docker was chosen over Podman for this project.

#### Package Management Strategy
**Decision: Use `uv` instead of pip/poetry/pipenv**

**Rationale:**
1. **Speed**: uv is 10-100x faster than pip for dependency resolution and installation
2. **Modern Tooling**: Built by Astral (creators of Ruff), designed for Python 3.11+ ecosystem
3. **Lock File Support**: `uv.lock` ensures reproducible builds across environments
4. **Docker Optimization**: Faster Docker image builds critical for iterative development
5. **Single Tool**: Replaces pip, pip-tools, and virtualenv with one command

**Implementation Rules:**
- `uv pip compile` generates `requirements.txt` from `pyproject.toml`
- Docker images use `uv pip install` for dependency installation
- `uv.lock` committed to version control for reproducibility
- Never use `pip install` directly (always through uv)

**Trade-offs Accepted:**
- Newer tool with smaller community vs pip/poetry (acceptable for personal project)
- Team members must install uv (minimal friction, single binary install)

#### Visualization Strategy
**Decision: Grafana for dashboards instead of custom web app (React/Next.js)**

**Rationale:**
1. **Time-to-Value**: Pre-built visualization components vs building charting from scratch
2. **SQL Native**: Grafana queries PostgreSQL directly - no API layer needed
3. **Dashboard Management**: Export/import JSON dashboards for version control
4. **Zero Frontend Code**: Focus development effort on ETL pipeline, not UI
5. **Battle-Tested**: Grafana is production-grade with extensive time-series support

**Implementation Rules:**
- Grafana connects to PostgreSQL via read-only user (security boundary)
- Dashboard definitions stored as JSON in `/grafana/dashboards/` directory
- Use PostgreSQL views for complex aggregations (created via Alembic)
- Custom panels only if built-in panels insufficient

**Trade-offs Accepted:**
- Limited customization vs custom React app (acceptable for personal dashboards)
- Grafana learning curve (offset by avoiding full-stack development)
- No mobile app (Grafana web UI responsive enough for personal use)

#### Repository Pattern Strategy
**Decision: Repository Pattern instead of direct ORM access in business logic**

**Rationale:**
1. **Testability**: Mock repository interfaces in unit tests without database
2. **Abstraction**: Business logic doesn't know about SQLAlchemy - easier to refactor
3. **Single Responsibility**: Repositories handle data access, services handle business rules
4. **Query Reusability**: Common queries (e.g., "find duplicate transactions") centralized
5. **Migration Safety**: If database schema changes, only repositories need updates

**Implementation Rules:**
- Define repository interfaces (abstract base classes)
- Implement concrete repositories using SQLAlchemy sessions
- Business logic depends on repository interfaces, not implementations
- One repository per aggregate root (e.g., `TransactionRepository`, `AccountRepository`)
- Repositories return domain models, not SQLAlchemy models (if domain layer exists)

**Trade-offs Accepted:**
- More boilerplate vs direct ORM usage (justified by testability gains)
- Indirection layer (acceptable for cleaner architecture)

**See Also**: [Repository Pattern Deep Dive](../docs/design_strategies/repository_pattern_strategy.md) for code examples showing testability benefits, query reusability patterns, and specific problems solved for this finance project.

#### Testing Strategy Justification
**Decision: Pytest with fixture-based testing and 80% coverage minimum**

**Rationale:**
1. **Financial Correctness**: Money calculations must be tested exhaustively - pytest fixtures allow data-driven tests
2. **Regression Prevention**: Bank statement formats change - comprehensive tests catch breakage early
3. **Confidence in Refactoring**: 80% coverage enables safe code improvements without fear
4. **Integration Testing**: Test containers (pytest-docker) verify database operations in isolation
5. **CI/CD Gate**: Tests as quality gate prevent broken code from merging

**Implementation Rules:**
- Unit tests for parsing logic (no database/filesystem dependencies)
- Integration tests for repository layer (test PostgreSQL container)
- Fixture files: anonymized bank PDFs representing different institutions
- Coverage checked in CI - PRs failing <80% blocked from merge
- Mock external dependencies (Docling API calls, filesystem operations)

**Trade-offs Accepted:**
- Time investment writing tests (essential for financial data correctness)
- Slower CI builds with integration tests (necessary for confidence)

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

## Additional Resources

### Design Strategy Documents
For in-depth explanations, code examples, and trade-off analysis for architectural decisions:

- **[Repository Pattern Strategy](../docs/design_strategies/repository_pattern_strategy.md)** - Why repository pattern is essential for testability, with before/after code examples demonstrating fast unit tests, query reusability, and clean separation of concerns
- **[Docker vs Podman Decision](../docs/design_strategies/docker_v_podman_strategy.md)** - Analysis of containerization choices comparing Docker Compose vs Podman, with rationale for Docker selection based on macOS development, Grafana compatibility, and community support

These documents provide the "why" behind major architectural decisions with concrete examples and use-case specific reasoning.