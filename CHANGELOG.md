# Changelog

All notable changes to the Finance Dashboard project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **v1.0 OpenSpec Documentation** [2026-01-07] - Complete planning for Scale & Reliability release
  - `openspec/V1.0_OVERVIEW.md` - High-level roadmap with all features and shared success criteria
  - 4 new change proposals with full specs and task checklists:
    - `v1.0-data-architecture` - Two-tier architecture (raw + analytics layers with materialized views)
    - `v1.0-database-performance` - Index optimization, connection pooling, query caching
    - `v1.0-bulk-processing` - Parallel PDF extraction, progress tracking, resume from failure
    - `v1.0-dashboard-improvements` - Account/date filtering, summary table queries, pagination
  - All proposals reference TOOLS.md and ROADMAP.md for context
  - Implementation order documented (dependency chain)

- Financial metrics extraction script (`scripts/analytics/extract_metrics.py`) - Extracts yearly and monthly summaries from CSV statements [2025-11-23]
  - Generates JSON output with total charges, payments, end-of-month balances
  - Supports running balance calculations across months
  - Output saved to `data/json/` directory

### Changed
- **Configuration Files Alignment with MVP Stack** [2026-01-07]
  - `Dockerfile`: Removed `pytest pytest-cov` (deferred to post-MVP), added `pdfplumber` (required for bank-specific processors)
  - `.env.example`: Fixed duplicate POSTGRES_PASSWORD entries, aligned with `.env` and `docker-compose.yml` for consistency
  - `TOOLS.md`: Already documented as source of truth for all tool versions and rationale
- **Project Reorganization** [2025-11-23]
  - Reorganized `scripts/` directory into categorized subdirectories:
    - `scripts/analytics/` - Data analysis and reporting scripts
    - `scripts/ingestion/` - Data ingestion workflows  
    - `scripts/debug/` - Debugging utilities
    - `scripts/maintenance/` - Backup/restore scripts (reserved)
  - Renamed `ingest.py` → `scripts/ingestion/ingest_data.py` for clarity
  - Moved `extract_metrics.py` → `scripts/analytics/extract_metrics.py`
  - Moved `debug_docling.py` → `scripts/debug/debug_docling.py`
  
- **Documentation Reorganization** [2025-11-23]
  - Reorganized `docs/` directory into clear categories:
    - `docs/versions/v0.1/` - Implementation retrospectives and walkthroughs (moved from `openspec_changes/`)
    - `docs/diataxis/` - Diataxis framework documentation
      - `how-to/` - Task-oriented guides (setup, troubleshooting)
      - `reference/` - Information-oriented docs (filename format)
      - `tutorials/`, `explanation/` - Reserved for future
    - `docs/openspec/` - Technical specs (BEFORE implementation, v0.3+)
  - Moved `troubleshooting.md` → `docs/diataxis/how-to/v0.1/troubleshooting.md`
  - Moved `spec_creation_summary_docs/` → `docs/versions/v0.1/implementation-summary.md`
  - Moved `filename-format.md` → `docs/diataxis/reference/filename-format.md`
  - Removed duplicate files and deprecated directories
  - Renamed `docs/next_features.md` → `ROADMAP.md` (moved to root for visibility)

---

## [0.1.0] - 2025-11-20

### Added
- Initial MVP release
- PDF extraction using Docling library
- Flexible CSV parser with heuristic column detection
- PostgreSQL database with transaction deduplication
- Grafana dashboards for spending visualization
- Docker Compose orchestration
- Automated processing script
- Security hardening (environment-based credentials)

### Features
- Process PDF and CSV financial statements
- Extract transactions with bank/card name from filename
- Store in PostgreSQL with deduplication
- Visualize in Grafana dashboards
- Support for multiple accounts (Citi, Amex)

### Documentation
- README.md with setup instructions
- How-to guides for environment setup and PDF processing
- OpenSpec technical documentation
- Troubleshooting guide

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.1.0 | 2025-11-20 | Initial MVP - Basic PDF to Grafana pipeline |
| 0.3 (Planned) | TBD | Complete Data Ingestion - Bank-specific PDF processors (Chase, Amex, Citi), load all historical statements |
| 0.5 (Planned) | TBD | Reserved for future feature |
| 0.7 (Planned) | TBD | Reserved for future feature |
| 0.9 (Planned) | TBD | Reserved for future feature |
| 1.0 (Planned) | TBD | Scale & Reliability - Two-tier data architecture, database optimization, dashboard improvements for 100k+ transactions |
| 2.0 (Planned) | TBD | Multi-Source Integration - Bank checking/savings, investment statements, transaction categorization |

---

**Note:** This changelog tracks changes starting from v0.1.0 (November 2025).
For detailed technical specifications, see `docs/openspec/` directory.
For version reports, see `docs/versions/` directory.
