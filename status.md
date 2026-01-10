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

## v0.3 - Complete Data Ingestion 🔄 In Progress

**Target:** January 2026

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
| Load all historical statements | Validate & ingest complete statement archive | ⬜ Not started |
| Fix any problematic files | Identify and resolve parsing failures | ⬜ Not started |
| Verify deduplication | Confirm no duplicates across imports | ⬜ Not started |
| Data integrity checks | Validate complete transaction history | ⬜ Not started |

### Success Criteria
- [ ] All 2024-2025 credit card statements loaded (Amex, Chase, Citi, etc.)
- [ ] Zero parsing failures for existing statements
- [ ] Duplicate detection working across all imports
- [ ] Complete transaction history in database

---

## v0.5, v0.7, v0.9 - Reserved 📋 TBD

**Status:** Placeholder for future feature releases

---

## v1.0 - Scale & Reliability 🚀 Planned

**Target:** Q1 2026

### Goals
1. Handle 100,000+ transactions without performance issues
2. Dashboard loads fast regardless of data size
3. Maintain query performance as data grows

### Planned Features

| Feature | Description |
|---------|-------------|
| Data Architecture for Scale | Two-tier architecture (raw + analytics layers with materialized views) |
| Database Performance | Indexes, partitioning, connection pooling, query caching |
| Bulk Processing | Parallel PDF extraction, progress tracking, resume from failure |
| Dashboard Improvements | Filters, date range presets, summary table queries, pagination |

### Success Criteria
- [ ] Process 100,000 transactions in < 5 minutes
- [ ] Dashboard loads in < 2 seconds with 100k+ rows
- [ ] Memory usage < 2GB during bulk import

---

## v2.0 - Multi-Source Integration 📊 Future

**Target:** Q2 2026

### Planned Features
- **Universal Ledger Schema** - Double-entry system to track transfers without duplicates
- **Bank Statement Parsers** - Chase checking, Bank of America, Wells Fargo, credit unions
- **Investment Statement Parsers** - Fidelity, Vanguard, Robinhood - trades, dividends, holdings
- **Smart Duplicate Detection** - Fuzzy matching to link related transactions
- **Advanced Dashboards** - Net worth, cash flow, investment performance

### Success Criteria
- All financial accounts integrated (checking, credit cards, investments)
- Zero duplicate transactions in unified ledger
- Net worth calculation accurate to within $100

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

### Supported Banks (v0.3+)
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
