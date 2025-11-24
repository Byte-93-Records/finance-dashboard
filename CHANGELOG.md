# Changelog

All notable changes to the Finance Dashboard project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Financial metrics extraction script (`scripts/analytics/extract_metrics.py`) - Extracts yearly and monthly summaries from CSV statements [2025-11-23]
  - Generates JSON output with total charges, payments, end-of-month balances
  - Supports running balance calculations across months
  - Output saved to `data/json/` directory

### Changed
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
    - `docs/openspec/` - Technical specs (BEFORE implementation, v0.2+)
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
| Unreleased | 2025-11-23 | Metrics extraction + project reorganization |

---

**Note:** This changelog tracks changes starting from v0.1.0 (November 2025).
For detailed technical specifications, see `docs/openspec/` directory.
For version reports, see `docs/versions/` directory.
