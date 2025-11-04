# Finance Dashboard

A self-hosted, privacy-focused personal finance tracking system that converts financial statement PDFs (bank statements, credit card statements, brokerage statements) into structured data for visualization and analysis.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Purpose

Finance Dashboard is a **privacy-first alternative** to cloud-based finance apps like Mint or Personal Capital. It runs entirely on your local machine, processing financial statements without sending your data to external services.

**Key Features:**
- 📄 Extract transaction data from PDF financial statements using Docling
- 🏦 Support for bank statements, credit card statements, and brokerage statements
- 💾 Store financial transactions in local PostgreSQL database
- 📊 Visualize data through Grafana dashboards
- 🐳 Run entirely in Docker containers for easy deployment
- 🔒 Zero external API calls - your data never leaves your machine

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     ETL Pipeline                        │
├─────────────────────────────────────────────────────────┤
│  Extract (PDF) → Transform (CSV) → Load (PostgreSQL)   │
└─────────────────────────────────────────────────────────┘

/data/pdfs/        →  pdf_processor/  →  /data/csv/
   (Input)              (Docling)         (Staging)
                            ↓
                      csv_parser/
                    (Validation)
                            ↓
                      database/
                   (SQLAlchemy ORM)
                            ↓
                    PostgreSQL 18
                            ↓
                       Grafana
                    (Dashboards)
```

## 🚀 Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (20+) or Docker Engine + Docker Compose (v2.0+)
- macOS, Linux, or Windows with WSL2

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Byte-93-Records/finance-dashboard.git
   cd finance-dashboard
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Create data directories:**
   ```bash
   mkdir -p data/{pdfs,csv,processed,failed}
   ```

4. **Start the stack:**
   ```bash
   docker-compose up -d
   ```

5. **Access Grafana:**
   - Open http://localhost:3000
   - Default credentials: `admin` / `admin` (change on first login)

### First Use

1. **Place PDF financial statements** in `data/pdfs/` directory
   - Bank statements (checking, savings)
   - Credit card statements
   - Brokerage statements (transaction history)

2. **Run PDF extraction:**
   ```bash
   docker-compose exec app python -m pdf_processor.cli process
   ```

3. **View your data** in Grafana dashboards at http://localhost:3000

## 📁 Directory Structure

```
finance-dashboard/
├── data/                      # Data storage (gitignored)
│   ├── pdfs/                 # Input: Place financial statement PDFs here
│   ├── csv/                  # Staging: Extracted CSVs before validation
│   ├── processed/            # Archive: Successfully processed PDFs
│   └── failed/               # Errors: Failed PDFs with error logs
├── pdf_processor/            # PDF extraction module
│   ├── extractor.py         # Docling integration
│   ├── validator.py         # CSV schema validation
│   ├── file_handler.py      # File operations
│   └── models.py            # Pydantic models
├── csv_parser/              # CSV parsing and validation
├── database/                # SQLAlchemy models and repositories
│   ├── models.py           # ORM models (accounts, transactions)
│   └── repositories/       # Repository pattern implementations
├── ingestion/              # ETL orchestration
├── grafana/               # Grafana configuration
│   └── dashboards/       # Dashboard JSON definitions
├── openspec/             # OpenSpec documentation
│   ├── project.md       # Project context and conventions
│   └── changes/         # Change proposals
└── docker-compose.yml   # Docker orchestration
```

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.11+ | Core application logic |
| **Database** | PostgreSQL 18 | Transaction storage |
| **PDF Processing** | Docling | PDF to CSV conversion |
| **Data Processing** | pandas, NumPy | Data transformation |
| **ORM** | SQLAlchemy + Alembic | Database access and migrations |
| **Visualization** | Grafana | Dashboards and analytics |
| **Containerization** | Docker & Docker Compose | Environment isolation |
| **Package Manager** | uv (by Astral) | Fast dependency management |
| **Testing** | pytest, pytest-cov | Unit and integration tests |

## 📊 Supported Financial Statement Formats

Finance Dashboard uses Docling's ML-based extraction to handle multiple financial statement formats:

**Bank Statements:**
- ✅ Chase Bank
- ✅ Bank of America
- ✅ Wells Fargo
- ✅ Citibank
- ✅ Capital One
- ✅ Most US banks with text-based PDF statements

**Credit Card Statements:**
- ✅ American Express
- ✅ Visa/Mastercard (various issuers)
- ✅ Discover
- ✅ Store credit cards

**Brokerage Statements:**
- ✅ Fidelity
- ✅ Charles Schwab
- ✅ TD Ameritrade
- ✅ E*TRADE
- ✅ Vanguard
- ✅ Most brokerage transaction histories

**Requirements:**
- Text-based PDFs (not scanned images)
- PDF size up to 50MB
- Standard tabular transaction format

## 🔒 Privacy & Security

**Privacy-First Design:**
- ✅ **Local-only processing** - No external API calls
- ✅ **No cloud services** - No Plaid, no external aggregators
- ✅ **Data ownership** - All data stored locally in PostgreSQL
- ✅ **No telemetry** - Zero analytics or tracking
- ✅ **Read-only PDFs** - Original statements never modified

**Security Best Practices:**
- Single-user design (no authentication required)
- PostgreSQL runs in isolated Docker container
- Grafana connects with read-only database user
- Environment variables for sensitive configuration

## 🧪 Development

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Docker Desktop

### Setup Development Environment

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Check coverage
pytest --cov=. --cov-report=html
```

### Code Quality

This project enforces strict code quality standards:

```bash
# Format code
black . --line-length 88

# Sort imports
isort .

# Type checking
mypy .

# Linting
flake8 .
```

**Standards:**
- PEP 8 compliance (enforced with Black)
- Type hints required (enforced with mypy)
- Docstrings required (Google style)
- 80% test coverage minimum
- Maximum function complexity: 10

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_pdf_processor.py

# Run integration tests only
pytest -m integration
```

## 📝 Configuration

### Environment Variables

Create a `.env` file (see `.env.example`):

```bash
# PostgreSQL Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=finance_dashboard
POSTGRES_USER=finance_user
POSTGRES_PASSWORD=your_secure_password

# PDF Processor Configuration
PDF_INPUT_DIR=/data/pdfs
CSV_OUTPUT_DIR=/data/csv
PROCESSED_DIR=/data/processed
FAILED_DIR=/data/failed
PDF_TIMEOUT_SECONDS=30

# Grafana Configuration
GRAFANA_PORT=3000
GRAFANA_ADMIN_PASSWORD=your_admin_password
```

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Run commands in app container
docker-compose exec app python -m pdf_processor.cli process

# Access PostgreSQL
docker-compose exec postgres psql -U finance_user -d finance_dashboard

# View Grafana logs
docker-compose logs -f grafana
```

## 📈 Usage

### Processing Financial Statements

1. **Place PDFs** in `data/pdfs/` directory
   - Bank statements (checking, savings, money market)
   - Credit card statements (monthly bills)
   - Brokerage statements (trades, dividends, capital gains)
   
2. **Run extraction:**
   ```bash
   docker-compose exec app python -m pdf_processor.cli process
   ```
3. **Check results:**
   - Successful: PDFs moved to `data/processed/`
   - Failed: PDFs moved to `data/failed/` with error logs
   - CSVs ready in `data/csv/` for ingestion

### Viewing Extraction Logs

```bash
# View processing summary
docker-compose logs app | grep "Processing complete"

# View failed extractions
ls -la data/failed/
cat data/failed/statement.pdf.error.log
```

### Creating Dashboards

Grafana dashboards are stored as JSON in `grafana/dashboards/`:

1. Create dashboard in Grafana UI
2. Export as JSON
3. Save to `grafana/dashboards/my-dashboard.json`
4. Commit to version control

## 🔧 Troubleshooting

### PDF Extraction Fails

**Issue:** PDFs moved to `data/failed/`

**Solutions:**
- Check error log: `cat data/failed/[filename].error.log`
- Verify PDF is text-based (not scanned image)
- Ensure PDF size is under 50MB
- Check Docker container logs: `docker-compose logs app`

### Database Connection Issues

**Issue:** Cannot connect to PostgreSQL

**Solutions:**
```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart PostgreSQL
docker-compose restart postgres

# Check connection from app container
docker-compose exec app psql -h postgres -U finance_user -d finance_dashboard
```

### Grafana Not Loading

**Issue:** Cannot access http://localhost:3000

**Solutions:**
```bash
# Check Grafana logs
docker-compose logs grafana

# Restart Grafana
docker-compose restart grafana

# Verify port not in use
lsof -i :3000
```

## 🤝 Contributing

Contributions are welcome! This project uses [OpenSpec](https://openspec.dev/) for spec-driven development.

### Before Contributing:

1. **Read project context:** [`openspec/project.md`](openspec/project.md)
2. **Check existing specs:** `openspec list --specs`
3. **Review active changes:** `openspec list`

### Creating a Change Proposal:

```bash
# Create new change proposal
openspec scaffold add-[feature-name]

# Validate proposal
openspec validate add-[feature-name] --strict

# Submit PR for review
```

See [`openspec/AGENTS.md`](openspec/AGENTS.md) for detailed contribution guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Docling](https://github.com/DS4SD/docling) - IBM Research's document processing library
- [uv](https://github.com/astral-sh/uv) - Astral's fast Python package manager
- [OpenSpec](https://openspec.dev/) - Spec-driven development framework

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/Byte-93-Records/finance-dashboard/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Byte-93-Records/finance-dashboard/discussions)
- **Documentation:** [Project Documentation](openspec/project.md)

## 🗺️ Roadmap

- [x] PDF to CSV extraction (Docling integration)
- [ ] CSV parsing and validation
- [ ] Database schema and migrations
- [ ] Transaction deduplication
- [ ] Grafana dashboard templates
- [ ] Automated transaction categorization
- [ ] Multi-currency support
- [ ] Budget tracking features
- [ ] Scheduled processing (APScheduler)
- [ ] Web UI for manual review

---

**Built with ❤️ for financial privacy and data ownership**