# Finance Dashboard - Feature Roadmap

This document outlines the planned features and improvements for the Finance Dashboard across multiple versions.

---

## v0.1 ✅ (Current - Nov 2025)
**Status:** Complete  
**Theme:** MVP - Basic PDF to Grafana Pipeline

### Delivered Features
- ✅ PDF extraction using Docling
- ✅ Flexible CSV ingestion with heuristic parsing
- ✅ PostgreSQL database with transaction deduplication
- ✅ Grafana dashboards (spending, transactions, stats)
- ✅ Bank/card name extraction from filenames
- ✅ Docker Compose orchestration
- ✅ Automated processing script
- ✅ Security hardening (no hardcoded credentials)

### Current State
- **Transactions:** 432 (Citi + Amex)
- **Date Range:** Jan 2024 - May 2025
- **Accounts:** 2 credit cards
- **Dashboards:** 1 primary finance dashboard

---

## v0.2 🎯 (Target: Dec 2025)
**Theme:** Scale & Performance - Production-Ready Data Pipeline

### Implementation Approach

> **⚠️ IMPORTANT:** All v0.2 features must follow the **OpenSpec Change Management Process**
> 
> **Process:**
> 1. Create OpenSpec proposal in `docs/openspec/v0.2/{feature-name}/`
> 2. Write technical specification with:
>    - Problem statement
>    - Proposed solution architecture
>    - API/interface changes
>    - Database schema updates
>    - Testing plan
> 3. Get review and approval
> 4. Implement changes in feature branch
> 5. Update version documentation in `docs/versions/v0.2/`
> 6. Update Diataxis how-to guides in `docs/how-to/v0.2/`
>
> **Documentation Structure:**
> ```
> docs/
> ├── openspec/v0.2/          # Technical specs (before implementation)
> ├── versions/v0.2/          # Version reports (after implementation)
> ├── how-to/v0.2/            # Diataxis how-to guides
> └── reference/v0.2/         # API/schema reference docs
> ```
>
> **Migration Task:**  
> As part of v0.2 kickoff, reorganize existing v0.1 documentation:
> - Move `docs/openspec_changes/*` → `docs/openspec/v0.1/`
> - Move `docs/version_reports/v0.1-*.md` → `docs/versions/v0.1/`
> - Keep existing how-to guides in `docs/how-to/v0.1/`
> - This ensures consistent structure across all versions

### Goals
- Process at least **1 year of data from ALL credit cards**
- Optimize database and Grafana performance for larger datasets

### Features

#### 1. Data Architecture Redesign
- **Problem:** Current schema stores all raw data in a single `transactions` table, which may become slow with 10K+ transactions
- **Solution:** Implement a **materialized view** or **summary tables** architecture
  ```
  Raw Data Layer (Archive):
  - transactions (original, immutable)
  - accounts
  - import_logs
  
  Analytics Layer (Grafana reads from this):
  - daily_spending_summary (aggregated by day/account)
  - monthly_spending_summary (aggregated by month/account/category)
  - merchant_summary (top merchants by spending)
  ```
- **Benefits:**
  - Faster Grafana queries (read from aggregated tables)
  - Preserve raw data for auditing
  - Better scalability for multi-year data

#### 2. Bank-Specific PDF Processors
- **Problem:** Generic Docling processor fails on complex PDFs (e.g., Amex) and produces unreliable results
- **Solution:** Route PDFs to bank-specific processors based on filename
  ```
  Architecture:
  pdf_processor/
  ├── router.py (detects bank from filename, routes to appropriate processor)
  ├── processors/
  │   ├── base_processor.py (abstract base class)
  │   ├── chase_processor.py (optimized for Chase)
  │   ├── amex_processor.py (handles Amex multi-line format)
  │   ├── citi_processor.py (Citi-specific extraction)
  │   ├── bofa_processor.py (Bank of America)
  │   ├── generic_processor.py (fallback using Docling)
  ```
- **Routing Logic:**
  1. Extract bank name from filename (e.g., `chase_sapphire_01_2025.pdf`)
  2. Check if bank-specific processor exists
  3. Use specific processor if available, otherwise fallback to generic
- **Processor Interface:**
  ```python
  class BasePDFProcessor:
      def can_process(self, pdf_path: Path) -> bool:
          """Check if this processor can handle the PDF"""
      
      def extract(self, pdf_path: Path, output_dir: Path) -> Path:
          """Extract to CSV, return CSV path"""
  ```
- **Benefits:**
  - Higher success rate (bank-specific optimization)
  - Faster processing (no complex ML/OCR if not needed)
  - Easier to debug (one processor per bank)
  - Community contributions (users can add their bank)
- **Example Implementation:**
  ```python
  class AmexProcessor(BasePDFProcessor):
      def can_process(self, pdf_path: Path) -> bool:
          """Check if this is an Amex PDF"""
          return "amex" in pdf_path.name.lower()
      
      def extract(self, pdf_path: Path, output_dir: Path) -> Path:
          """Extract Amex PDF using pdfplumber (works better than Docling for Amex)"""
          import pdfplumber
          
          transactions = []
          with pdfplumber.open(pdf_path) as pdf:
              for page in pdf.pages:
                  # Amex-specific table extraction logic
                  tables = page.extract_tables()
                  for table in tables:
                      # Parse Amex's multi-line description format
                      # Handle their specific date format
                      # Skip header/footer rows
                      transactions.extend(self._parse_amex_table(table))
          
          # Write to CSV
          csv_path = output_dir / f"{pdf_path.stem}.csv"
          self._write_csv(transactions, csv_path)
          return csv_path
  ```

#### 3. Bulk Processing Improvements
- Process multiple PDFs/CSVs in parallel
- Add progress bar and ETA for large batches
- Implement incremental updates (only process new files)
- Add file hash tracking to prevent duplicate imports

#### 4. Performance Optimization
- Add database indexes on frequently queried columns:
  - `transaction_date`
  - `account_id`
  - `transaction_type`
- Implement query caching in Grafana
- Optimize SQL queries with EXPLAIN ANALYZE

#### 5. Data Validation & Quality
- Add data quality checks:
  - Detect and flag anomalies (unusual amounts, missing descriptions)
  - Identify potential duplicate transactions across accounts
  - Validate date ranges (warn if importing old data)
- Generate data quality report after ingestion

#### 6. Enhanced Grafana Dashboards
- Add filters/variables:
  - Account selector (dropdown)
  - Date range presets (Last Month, Last Quarter, YTD)
  - Bank/Card filter
- New panels:
  - Monthly spending trend line
  - Top 10 merchants by spend
  - Week-over-week comparison
- Performance optimizations for large datasets

#### 7. Backup & Restore
- **Automated Backup Scripts:**
  ```bash
  scripts/backup.sh         # Backup PostgreSQL + Grafana
  scripts/restore.sh        # Restore from backup
  ```
- **Backup Components:**
  - PostgreSQL database dump (SQL format)
  - Grafana dashboards and settings (JSON export)
  - Docker volume snapshots
  - Configuration files (.env, docker-compose.yml)
- **Storage Options:**
  - Local backup directory (`backups/YYYY-MM-DD/`)
  - Cloud storage (S3, Google Drive) integration
  - Automated daily/weekly backup schedule
- **Restore Process:**
  - One-command restore from any backup point
  - Verification after restore
  - Support for selective restore (DB only, Grafana only)
- **Example:**
  ```bash
  # Create backup
  ./scripts/backup.sh
  # Output: backups/2025-11-20/
  #   ├── postgres_dump.sql
  #   ├── grafana_export.json
  #   └── config_backup.tar.gz
  
  # Restore from backup
  ./scripts/restore.sh backups/2025-11-20/
  ```

#### 8. Financial Metrics Extraction
- **Problem:** Need quick access to key financial metrics (balances, totals) without querying the database
- **Solution:** Generate JSON summary reports with important metrics
- **Features:**
  - Extract yearly summaries:
    - Total charges for the year
    - Total payments for the year
    - End-of-year balance
    - Transaction count
  - Monthly breakdowns:
    - End-of-month balance (running total)
    - Monthly charges
    - Monthly payments
    - Transaction count per month
- **Output Format:**
  ```json
  {
    "summary": {
      "year": 2024,
      "total_charges": 9564.37,
      "total_payments": 9565.34,
      "end_of_year_balance": -0.97,
      "transaction_count": 392
    },
    "monthly_balances": {
      "2024-01": {
        "end_of_month_balance": -1.35,
        "charges": 1273.74,
        "payments": 1275.09,
        "transaction_count": 49
      }
    }
  }
  ```
- **Use Cases:**
  - Quick financial health checks
  - Export data for tax preparation
  - Integration with other tools/spreadsheets
  - Backup of key metrics outside the database
- **Implementation:**
  - Python script to parse CSV and generate JSON
  - Command-line tool: `python extract_metrics.py [csv_file]`
  - Output saved to `data/json/` directory
- **Example:**
  ```bash
  python extract_metrics.py
  # Output: data/json/amex_bluecash_2024_metrics.json
  ```

### Success Metrics
- ✅ Process 10,000+ transactions without performance degradation
- ✅ Grafana dashboard load time < 2 seconds
- ✅ All credit card data from 2024 ingested
- ✅ Zero duplicate transaction imports

### Technical Debt to Address
- Improve error handling in PDF extraction
- Add comprehensive unit tests for ingestion logic
- Document database schema with ER diagrams
- Create performance benchmarking script

---

## v0.3 🚀 (Target: Q1 2026)
**Theme:** Multi-Source Integration - Complete Financial Picture

### Goals
- Integrate **bank statements** (checking/savings accounts)
- Integrate **investment statements** (Fidelity, Vanguard, etc.)
- Redesign database schema for unified ledger
- Eliminate duplicate transaction issues across accounts

### Features

#### 1. Universal Ledger Schema
- **Problem:** Current schema treats each account separately, causing duplicates (e.g., credit card payment shows in both checking and credit card)
- **Solution:** Implement a **double-entry ledger** system
  ```
  New Schema:
  - ledger_entries (all financial movements)
    - id, date, description, amount, account_from, account_to
  - accounts (checking, savings, credit, investment, cash)
  - transaction_links (track related entries, e.g., transfer or payment)
  ```
- **Benefits:**
  - Eliminate duplicates by linking related transactions
  - True net worth calculation
  - Cash flow tracking (income vs expenses)

#### 2. Bank Statement Support
- Add parsers for common bank formats:
  - Chase checking/savings
  - Bank of America
  - Wells Fargo
  - Credit unions (CSV formats)
- Support for different transaction types:
  - Deposits (salary, transfers in)
  - Withdrawals (ATM, checks, transfers out)
  - Fees and interest

#### 3. Investment Statement Integration
- Add support for:
  - **Fidelity** (stocks, ETFs, mutual funds)
  - **Vanguard** (retirement accounts)
  - **Robinhood** (trading activity)
- Track investment transactions:
  - Buy/sell orders
  - Dividends and capital gains
  - Account value snapshots
- New dashboards:
  - Portfolio performance
  - Asset allocation
  - Dividend income tracking

#### 4. Smart Duplicate Detection
- Implement ML-based duplicate detection:
  - Fuzzy matching on descriptions
  - Date proximity (±3 days)
  - Amount matching (exact or inverse)
- User interface to:
  - Review potential duplicates
  - Mark transactions as linked (e.g., payment)
  - Confirm or reject matches

#### 5. Advanced Dashboards
- **Net Worth Dashboard:**
  - Assets (checking, savings, investments)
  - Liabilities (credit cards, loans)
  - Net worth trend over time
- **Cash Flow Dashboard:**
  - Income vs Expenses
  - Savings rate
  - Burn rate analysis
- **Investment Dashboard:**
  - Portfolio value over time
  - Returns (daily, monthly, YTD)
  - Asset allocation pie chart

### Success Metrics
- ✅ All financial accounts integrated (3+ checking, 3+ credit cards, 2+ investment)
- ✅ Zero duplicate transactions in unified ledger
- ✅ Net worth calculation accurate to within $100
- ✅ Full year of investment data tracked

### Migration Plan
- Create migration script to convert v0.2 data to ledger format
- Run parallel systems during transition period
- Validate data integrity before cutover

---

## v0.4 🤖 (Target: Q2 2026)
**Theme:** Intelligence Layer - ML-Powered Insights

### Goals
- Automated transaction categorization using ML
- Predictive spending analytics
- Anomaly detection
- Personalized insights

### Features

#### 1. ML-Based Categorization
- **Training Data:**
  - Seed with common merchant-to-category mappings
  - Learn from user corrections
  - Use merchant name, amount, date patterns
- **Categories:**
  - Groceries, Dining, Transportation, Entertainment
  - Utilities, Healthcare, Shopping, Travel
  - Subscriptions, Income, Transfers
- **Model:**
  - Use scikit-learn or lightweight transformer model
  - Fine-tune on user's historical data
  - Achieve 90%+ accuracy

#### 2. Smart Merchant Recognition
- Build merchant database:
  - Normalize names (e.g., "TST*ANNAPOORNA" → "Annapoorna Restaurant")
  - Extract location from descriptions
  - Link to business categories
- Features:
  - Auto-complete for manual entry
  - Merchant spending history
  - Favorite merchants tracking

#### 3. Predictive Analytics
- **Monthly Budget Predictions:**
  - Forecast next month's spending by category
  - Account for seasonality (holidays, tax season)
  - Alert when exceeding predicted spend
- **Subscription Detection:**
  - Identify recurring charges
  - Calculate annual cost
  - Suggest cancellation candidates

#### 4. Anomaly Detection
- Flag unusual transactions:
  - Large purchases (>2x std dev)
  - New merchants
  - Foreign transactions
  - Duplicate charges
- Real-time alerts (email or dashboard)

#### 5. Advanced Dashboards
- **Category Breakdown:**
  - Pie chart of spending by category
  - Category trends over time
  - Budget vs actual comparison
- **Insights Panel:**
  - "You spent 20% more on dining this month"
  - "Potential duplicate charge detected"
  - "You're on track to save $X this month"
- **Subscription Tracker:**
  - List all recurring charges
  - Annual cost calculation
  - Cancellation recommendations

#### 6. API & Data Export
- REST API for programmatic access
- Export to CSV, JSON, Excel
- Integration with accounting software (QuickBooks, Mint)

### Success Metrics
- ✅ 90%+ accuracy on transaction categorization
- ✅ All subscriptions automatically detected
- ✅ Users save 5+ hours/month on manual categorization
- ✅ Budget predictions within 10% of actual

### Technical Requirements
- Add ML inference service (Python FastAPI)
- Implement feature engineering pipeline
- Set up model training and evaluation workflow
- Create feedback loop for continuous improvement

---

## v0.5+ 🌟 (Future Vision)
**Theme:** Ecosystem & Automation

### Potential Features

#### 1. Real-Time Bank Integration
- **Plaid API Integration:**
  - Automatic transaction sync
  - Balance updates
  - Account linking
- **Open Banking Support:**
  - Direct bank API connections
  - Real-time notifications

#### 2. Mobile Application
- React Native or Flutter app
- Features:
  - View dashboards on mobile
  - Scan and upload receipts
  - Quick expense entry
  - Push notifications for anomalies

#### 3. Multi-User & Household Support
- User authentication (OAuth)
- Shared household view
- Individual vs shared expense tracking
- Split transaction support

#### 4. Advanced AI Features
- **Natural Language Queries:**
  - "How much did I spend on groceries last month?"
  - "Show me all transactions over $100"
- **Smart Budgeting:**
  - AI suggests budget based on historical patterns
  - Adaptive budgets that adjust monthly
- **Tax Optimization:**
  - Identify tax-deductible expenses
  - Generate reports for CPA
  - Cryptocurrency tax tracking

#### 5. Gamification & Goals
- Savings challenges
- Spending streaks (e.g., "No dining out for 7 days")
- Achievement badges
- Social comparison (anonymous benchmarks)

#### 6. Integration Ecosystem
- **IFTTT/Zapier Integration:**
  - Trigger actions based on transactions
  - Example: "When I spend >$100, send me a text"
- **Smart Home Integration:**
  - Link with utility bills
  - Track energy usage vs cost
- **Calendar Integration:**
  - See spending alongside events
  - Budget alerts before planned trips

---

## Development Principles

### Code Quality
- Maintain 80%+ test coverage
- Use type hints throughout
- Follow PEP 8 style guide
- Document all public APIs

### Performance
- Keep dashboard load times < 2s
- Optimize for 100K+ transactions
- Cache aggressively
- Profile regularly

### Security
- Never store credentials in code
- Encrypt sensitive data at rest
- Use HTTPS for all API calls
- Regular security audits

### User Experience
- Keep UI simple and intuitive
- Provide clear error messages
- Offer tutorials and tooltips
- Optimize for speed

---

## How to Contribute

We welcome contributions! To suggest new features:
1. Open an issue with `[Feature Request]` tag
2. Describe the use case and benefit
3. Propose implementation approach
4. Tag with target version (v0.2, v0.3, etc.)

---

## Version History

| Version | Release Date | Theme | Status |
|---------|-------------|-------|--------|
| v0.1 | Nov 2025 | MVP - Basic Pipeline | ✅ Complete |
| v0.2 | Dec 2025 | Scale & Performance | 🎯 Planned |
| v0.3 | Q1 2026 | Multi-Source Integration | 🚀 Planned |
| v0.4 | Q2 2026 | ML-Powered Insights | 🤖 Planned |
| v0.5+ | TBD | Ecosystem & Automation | 🌟 Vision |

---

**Last Updated:** November 20, 2025  
**Current Version:** v0.1
