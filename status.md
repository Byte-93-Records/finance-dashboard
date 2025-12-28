# Finance Dashboard - Project Status

**Last Updated:** December 28, 2025

---

## v0.1 - MVP Pipeline ✅ Complete

**Released:** November 2025

### What Was Built
- **PDF Extraction**: Docling-based extraction converting bank statement PDFs to CSV
- **Heuristic CSV Parsing**: Smart column detection (dates, amounts, descriptions) via `ingest.py`
- **PostgreSQL Database**: Transaction storage with SHA-256 deduplication
- **Grafana Dashboards**: Spending trends, transaction list, daily spending charts
- **Docker Compose**: Full stack orchestration (PostgreSQL, Grafana, Python app)
- **Automation Script**: `scripts/process-and-view.sh` for end-to-end processing

### Data Ingested
- 432 transactions across 2 accounts (Citi ThankYou, Amex Blue Cash)
- Date range: January 2024 - May 2025

### Known Limitations
- Docling failed on complex PDFs (Amex yearly statements, Chase)
- Generic column detection, no bank-specific handling

---

## v0.2 - Scale & Reliability 🔄 In Progress

**Target:** December 2025

### Completed ✅

#### Bank-Specific PDF Processors
Router-based architecture that selects the right extraction method per bank:

```
PDF → Router (filename detection) → Bank Processor → CSV
                                         │
              ┌──────────────────────────┼──────────────────────────┐
              │                          │                          │
        AmexProcessor              ChaseProcessor            GenericProcessor
        (pdfplumber)               (pdfplumber)                 (Docling)
```

| Processor | Method | Status | Transactions Tested |
|-----------|--------|--------|---------------------|
| AmexProcessor | Text extraction (pdfplumber) | ✅ Working | 339 |
| ChaseProcessor | Text extraction (pdfplumber) | ✅ Working | 72 |
| CitiProcessor | Docling (delegates to generic) | ✅ Created | Pending test |
| GenericProcessor | Docling (fallback) | ✅ Working | - |

**Files Added:**
- `pdf_processor/router.py`
- `pdf_processor/processors/base.py`
- `pdf_processor/processors/amex.py`
- `pdf_processor/processors/chase.py`
- `pdf_processor/processors/citi.py`
- `pdf_processor/processors/generic.py`

### Remaining

| Feature | Purpose | Status |
|---------|---------|--------|
| Database indexes | Performance for 100k+ transactions | ⬜ Not started |
| Summary tables / materialized views | Fast Grafana queries | ⬜ Not started |
| Table partitioning | Efficient date-range queries | ⬜ Not started |
| Bulk processing | Parallel PDF processing, progress bars | ⬜ Not started |
| Dashboard improvements | Filters, presets, new panels | ⬜ Not started |
| Documentation | Processor docs, adding new banks | ⬜ Not started |

### Success Criteria
- [ ] Process 100,000 transactions in < 5 minutes
- [ ] Dashboard loads in < 2 seconds with 100k+ rows
- [ ] All 2024 credit card data from all cards ingested
- [ ] Zero duplicate imports across re-runs

---

## v0.3 - Multi-Source Integration 📋 Planned

**Target:** Q1 2026

### Goals
- Integrate bank statements (checking/savings accounts)
- Integrate investment statements (Fidelity, Vanguard, Robinhood)
- Unified ledger to eliminate duplicate transactions

### Planned Features

| Feature | Description |
|---------|-------------|
| Universal Ledger Schema | Double-entry system to track transfers without duplicates |
| Bank Statement Parsers | Chase checking, Bank of America, Wells Fargo, credit unions |
| Investment Statement Parsers | Fidelity, Vanguard, Robinhood - trades, dividends, holdings |
| Smart Duplicate Detection | Fuzzy matching to link related transactions (e.g., credit card payment from checking) |
| Advanced Dashboards | Net worth, cash flow, investment performance |

### Success Criteria
- All financial accounts integrated (checking, credit cards, investments)
- Zero duplicate transactions in unified ledger
- Net worth calculation accurate to within $100

---

## v0.4 - Intelligence Layer 🤖 Future

**Target:** Q2 2026

### Planned Features
- **ML-Based Categorization**: Auto-categorize transactions by merchant
- **Smart Merchant Recognition**: Normalize merchant names (e.g., "TST*STARBUCKS" → "Starbucks")
- **Predictive Analytics**: Monthly spending forecasts, subscription detection
- **Anomaly Detection**: Flag unusual transactions, potential duplicates
- **Category Dashboards**: Spending by category, budget vs actual

---

## v0.5+ - Ecosystem 🌟 Vision

### Potential Features
- Real-time bank sync (Plaid API)
- Mobile application
- Multi-user / household support
- Natural language queries ("How much did I spend on groceries?")
- Tax optimization reports

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        PDF Files                            │
│              (bank statements, credit cards)                │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      PDF Router                             │
│         (selects processor based on filename)               │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │  Amex    │    │  Chase   │    │ Generic  │
    │Processor │    │Processor │    │(Docling) │
    └────┬─────┘    └────┬─────┘    └────┬─────┘
         └───────────────┼───────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      CSV Files                              │
│     (transaction_date, description, amount, type)           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     ingest.py                               │
│          (heuristic parsing, deduplication)                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL                               │
│         (accounts, transactions, import_logs)               │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      Grafana                                │
│              (dashboards, visualizations)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

### Process New PDFs
```bash
# Place PDFs in data/pdfs/ with naming: bank_card_month_year.pdf
./scripts/process-and-view.sh
```

### View Dashboard
```
http://localhost:3000
```

### Supported Banks (v0.2)
| Bank | Filename Pattern | Processor |
|------|------------------|-----------|
| Amex | `amex_*.pdf` | AmexProcessor |
| Chase | `chase_*.pdf`, `freedom_*.pdf`, `sapphire_*.pdf` | ChaseProcessor |
| Citi | `citi_*.pdf`, `thankyou_*.pdf` | CitiProcessor (Docling) |
| Other | `*` | GenericProcessor (Docling) |

### Add a New Bank Processor
1. Create `pdf_processor/processors/{bank}.py`
2. Implement `can_process(pdf_path)` and `extract(pdf_path, output_dir)`
3. Add to router's processor list in `router.py`
4. Test with sample statements
