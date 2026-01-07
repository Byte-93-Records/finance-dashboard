# Project Tools & Dependencies

Complete tooling requirements for the Finance Dashboard MVP, organized by purpose.

## Package Management

| Tool | Version | Purpose | Why |
|------|---------|---------|-----|
| **uv** | Latest | Python package installer & resolver | 10-100x faster than pip, reproducible builds with `uv.lock` |

Install: `brew install uv` or see https://github.com/astral-sh/uv

## Core Runtime

| Tool | Version | Constraint | Purpose |
|------|---------|-----------|---------|
| **Python** | 3.11+ | Required | Language runtime |
| **PostgreSQL** | 18 | Required via Docker | Relational database (financial data) |

## Python Dependencies (pyproject.toml)

### PDF Processing
| Package | Version | Purpose |
|---------|---------|---------|
| **docling** | ≥2.0.0 | ML-based PDF document extraction (fallback) |
| **pdfplumber** | ≥0.10.0 | Precise table extraction for bank-specific processors |

### Data Processing
| Package | Version | Purpose |
|---------|---------|---------|
| **pandas** | ≥2.0.0 | Data manipulation & analysis |
| **pydantic** | ≥2.0.0 | Data validation (TransactionRow models) |

### Database
| Package | Version | Purpose |
|---------|---------|---------|
| **sqlalchemy** | ≥2.0.0 | ORM for PostgreSQL (no raw SQL) |
| **psycopg2-binary** | ≥2.9.0 | PostgreSQL driver |
| **alembic** | ≥1.13.0 | Database schema versioning & migrations |

### CLI & Orchestration
| Package | Version | Purpose |
|---------|---------|---------|
| **click** | ≥8.0.0 | Command-line interface framework |

### Configuration & Logging
| Package | Version | Purpose |
|---------|---------|---------|
| **python-dotenv** | ≥1.0.0 | Environment variable management |
| **structlog** | ≥24.0.0 | Structured logging for debugging |

## Infrastructure

| Tool | Version | Purpose | Why |
|------|---------|---------|-----|
| **Docker** | 20+ | Container runtime | Reproducible environment, isolated services |
| **Docker Compose** | 2.0+ | Multi-container orchestration | Coordinate Python, PostgreSQL, Grafana |
| **Grafana** | Latest | Visualization & dashboards | Pre-built financial analytics (no custom frontend code) |

## Deferred (Post-MVP)

| Tool | Purpose | Version |
|------|---------|---------|
| APScheduler | Scheduled PDF processing (v2) | ≥3.0.0 |
| pytest | Unit & integration tests (future) | ≥7.0.0 |
| pytest-cov | Coverage reporting (future) | ≥4.0.0 |

## Installation Guide

### Prerequisites
```bash
# Install Python 3.11+
python3 --version  # Should be 3.11+

# Install uv (fast package manager)
brew install uv

# Install Docker & Docker Compose
# Download from https://www.docker.com/products/docker-desktop
```

### Project Setup
```bash
# Navigate to project
cd ~/Documents/Git/GitHub/finance-dashboard

# Install Python dependencies via uv
uv pip install -r requirements.txt

# Or compile from pyproject.toml
uv pip compile pyproject.toml -o requirements.txt
uv pip install -r requirements.txt

# Verify installations
python3 --version
uv --version
docker --version
docker-compose --version
```

### Start Services
```bash
# Build & start all services (Python, PostgreSQL, Grafana)
docker-compose up -d

# Verify services are running
docker-compose ps
```

## Configuration Files

| File | Purpose |
|------|---------|
| **pyproject.toml** | Python dependencies & project metadata |
| **uv.lock** | Locked dependency versions (reproducible builds) |
| **requirements.txt** | Generated from pyproject.toml via `uv pip compile` |
| **docker-compose.yml** | Service definitions (Python, PostgreSQL, Grafana) |
| **.env** | Runtime configuration (database URL, API keys) |
| **.env.example** | Template for .env (checked into git) |

## Why This Stack?

**Lean & Focused on Goal:**
- Docling + pdfplumber = handle real PDFs (not just idealized CSVs)
- SQLAlchemy + Alembic = maintainable database schema evolution
- Grafana = skip frontend code, focus on data pipeline
- Click = minimal CLI framework (not full framework bloat)
- uv + Docker = reproducible, fast, consistent across machines

**No Bloat:**
- No NumPy (pandas handles data; only use NumPy for heavy math)
- No pytest/coverage (validate manually for MVP)
- No ORM-level testing frameworks (test via Docker Postgres)
- No web framework (Grafana handles visualization)

---

**Last Updated:** 2026-01-07
**Status:** MVP (v0.1.0)
