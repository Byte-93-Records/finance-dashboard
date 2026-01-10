# Finance Dashboard - Roadmap

## v0.1 (Complete - Nov 2025)

**Theme:** MVP - Basic PDF to Grafana Pipeline

### What Works
- PDF extraction via Docling with heuristic CSV parsing
- PostgreSQL database with transaction deduplication (SHA-256 hashing)
- Grafana dashboard with spending trends and transaction list
- Bank/card name extraction from filenames
- Docker Compose orchestration
- Automated processing script (`scripts/process-and-view.sh`)

### Current Data
- 432 transactions across 2 accounts (Citi ThankYou, Amex Blue Cash)
- Date range: Jan 2024 - May 2025

---

## v0.3 (Next)

**Theme:** Complete Data Ingestion - Bank-Specific PDF Processors

### Goals
1. Extract transactions reliably from all major credit card PDFs (Amex, Chase, Citi)
2. Load all historical statements into database
3. Eliminate parsing failures from generic Docling

### Features

#### 1. Bank-Specific PDF Processors
**Problem:** Generic Docling fails on complex PDFs (Amex multi-line, Chase tables)

**Solution:** Router-based processor selection:
```
pdf_processor/
├── router.py              # Detects bank from filename, routes to processor
└── processors/
    ├── base.py            # Abstract base class
    ├── chase.py           # Chase-specific (pdfplumber)
    ├── amex.py            # Amex-specific (pdfplumber)
    ├── citi.py            # Citi-specific
    └── generic.py         # Fallback (Docling)
```

Routing: `chase_sapphire_01_2025.pdf` → `ChaseProcessor`

#### 2. Data Loading
- Validate and load all historical PDFs/CSVs
- Identify and fix any problematic files
- Confirm deduplication across re-runs
- Verify data integrity

### Success Criteria
- [ ] All 2024-2025 credit card statements loaded (Amex, Chase, Citi, etc.)
- [ ] Zero parsing failures for existing statements
- [ ] Duplicate detection working across all imports
- [ ] Complete transaction history in database

---

## v0.5 (Future)

**Theme:** Data Quality & Validation

Ensure imported data is accurate before scaling. Add validation rules, duplicate detection improvements, and data integrity checks.

- Transaction validation (date ranges, amount formats, required fields)
- Improved duplicate detection (fuzzy matching for similar transactions)
- Data quality reports (missing data, anomalies, parsing issues)

---

## v0.7 (Future)

**Theme:** Performance Foundations

Lay groundwork for v1.0 scale. Add essential indexes and optimize critical queries without full architecture changes.

- Database indexes on high-query columns (date, account, amount)
- Query optimization for existing Grafana panels
- Basic connection pooling setup

---

## v0.9 (Future)

**Theme:** CLI & Workflow Improvements

Improve developer experience and operational tooling before v1.0 feature expansion.

- Enhanced CLI with progress bars and better error messages
- Dry-run mode for imports (preview without committing)
- Basic logging and import history tracking

---

## v1.0 (Future)

**Theme:** Scale & Reliability - 100k+ Transaction Support

### Goals
1. Handle 100,000+ transactions without performance issues
2. Dashboard loads fast regardless of data size
3. Maintain query performance as data grows

### Features

#### 1. Data Architecture for Scale

**Problem:** Current single `transactions` table won't perform well at 100k+ rows

**Solution:** Two-tier architecture:

```
Raw Layer (Archive, immutable):
├── transactions          # All raw transactions
└── import_logs           # Import history

Analytics Layer (Grafana reads from this):
├── daily_summary         # Aggregated by day/account
├── monthly_summary       # Aggregated by month/account/category
└── merchant_summary      # Top merchants by spending
```

**Implementation:**
- Materialized views refreshed after each import
- Grafana queries ONLY the summary tables
- Raw transactions for drill-down/search only
- Partition `transactions` table by year

#### 2. Database Performance
- Add indexes: `transaction_date`, `account_id`, `transaction_hash`
- Partition transactions by year: `transactions_2023`, `transactions_2024`, etc.
- Connection pooling for concurrent queries
- Query caching in Grafana (1-5 min TTL)

#### 3. Bulk Processing
- Process multiple PDFs in parallel (configurable workers)
- Progress bar with ETA for large batches
- Resume from failure (track processed file hashes)
- Memory-efficient streaming (don't load all PDFs at once)

#### 4. Dashboard Improvements
- Account dropdown filter (query accounts table)
- Date range presets (Last Month, Quarter, YTD, Custom)
- Panels read from summary tables for speed:
  - Monthly spending trend (from `monthly_summary`)
  - Top 10 merchants (from `merchant_summary`)
  - Daily spending heatmap (from `daily_summary`)
- Transaction search panel (queries raw table with pagination)

### Success Criteria
- [ ] Process 100,000 transactions in < 5 minutes
- [ ] Dashboard loads in < 2 seconds with 100k+ rows
- [ ] Zero duplicate imports across re-runs
- [ ] Memory usage < 2GB during bulk import

---

## v2.0 (Future)

**Theme:** Multi-Source Integration

### Potential Features
- Bank statements (checking/savings) - different format than credit cards
- Investment statements (Fidelity, Vanguard, Robinhood)
- Double-entry ledger schema (eliminates duplicates from transfers)
- Transaction categorization (rule-based or ML)

---

## Development Notes

### Architecture Decision: Summary Tables vs Raw Queries

**Why summary tables?**
- Grafana querying 100k rows per panel = slow
- Pre-aggregated summaries: O(1) query time
- Raw table preserved for audit/search

**Refresh strategy:**
- After each import: `REFRESH MATERIALIZED VIEW CONCURRENTLY`
- Or: Trigger-based incremental updates

### Adding a New Bank Processor
1. Create `pdf_processor/processors/{bank}.py`
2. Implement `can_process(pdf_path)` and `extract(pdf_path, output_dir)`
3. Add to router's processor list
4. Test with sample statements

### Running Tests
```bash
docker compose run --rm app pytest tests/ -v
```

### Processing New Statements
```bash
# Place PDFs in data/pdfs/ with format: bank_card_month_year.pdf
./scripts/process-and-view.sh
```

### Benchmarking
```bash
# Generate test data
python scripts/generate_test_data.py --transactions 100000

# Time import
time python ingest.py --all

# Check query performance
docker compose exec postgres psql -U finance -d finance_db -c "EXPLAIN ANALYZE SELECT * FROM monthly_summary;"
```
