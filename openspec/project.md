# Project Context

## Purpose

Personal finance tracking system that converts PDF financial statements into structured data for visualization. The system:
- Extracts transaction data from PDF statements using Docling
- Stores transactions in PostgreSQL with deduplication
- Visualizes data through Grafana dashboards
- Runs entirely in Docker for easy deployment

**Key constraint:** Privacy-first, local-only. No external APIs, no cloud services.

## Tech Stack

- **Language:** Python 3.11+
- **Database:** PostgreSQL 18 (Docker)
- **PDF Processing:** Docling (ML-based extraction)
- **Data Processing:** pandas
- **Visualization:** Grafana 11.4
- **Containerization:** Docker Compose
- **Package Manager:** uv

## Current Architecture (v0.1)

```
PDF files → Docling → CSV → Heuristic Parser → PostgreSQL → Grafana
           (extract)       (ingest.py)
```

### Key Files
- `pdf_processor/` - Docling-based PDF extraction
- `ingest.py` - Heuristic CSV parsing and database loading
- `csv_parser/filename_parser.py` - Bank/card extraction from filenames
- `database/models.py` - SQLAlchemy models (accounts, transactions)
- `grafana/dashboards/` - Dashboard JSON definitions
- `scripts/process-and-view.sh` - End-to-end automation

### Data Flow
1. Place PDFs in `data/pdfs/` (format: `bank_card_month_year.pdf`)
2. Run processing script
3. View in Grafana at http://localhost:3000

## Code Conventions

### Style
- PEP 8 with Black formatter (line length: 88)
- Type hints for function signatures
- Google-style docstrings for public functions
- Imports: stdlib → third-party → local (isort)

### Database
- SQLAlchemy ORM (no raw SQL)
- Alembic for migrations
- Financial amounts: `NUMERIC`/`Decimal` (never float)
- Transaction deduplication via SHA-256 hash

### Git
- `main` - production-ready
- `feature/*` - new features
- `fix/*` - bug fixes
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`

## Constraints

- **Single user** - no authentication
- **Local only** - no external API calls
- **Read-only PDFs** - never modify source files
- **Idempotent imports** - same PDF won't duplicate transactions
- **Docker required** - entire stack via `docker-compose up`

## What's Planned (v0.2)

See `/ROADMAP.md` for details. Key priorities:
1. Bank-specific PDF processors (Amex, Chase, Citi)
2. Summary tables for 100k+ transaction performance
3. Improved Grafana dashboards
