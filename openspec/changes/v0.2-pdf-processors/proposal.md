# Proposal: Bank-Specific PDF Processors

## Why

The current Docling-based PDF extractor fails on complex bank statements:
- **Amex**: Multi-line descriptions get split across rows
- **Chase**: Table detection misses transaction tables
- **Complex layouts**: Headers/footers get mixed into data

Result: Only ~50% of PDFs process successfully. Users must manually export CSVs from bank websites as a workaround.

## What Changes

Add a router-based processor architecture that selects the right extraction method per bank:

```
PDF → Router (detect bank from filename) → Bank-Specific Processor → CSV
                                        ↓
                         ┌──────────────┴──────────────┐
                         │                             │
                    AmexProcessor              GenericProcessor
                    (pdfplumber)                  (Docling)
```

**New components:**
- `router.py` - Detects bank from filename, routes to processor
- `processors/base.py` - Abstract base class defining interface
- `processors/amex.py` - Amex-specific extraction (pdfplumber)
- `processors/chase.py` - Chase-specific extraction
- `processors/citi.py` - Citi-specific extraction
- `processors/generic.py` - Fallback using existing Docling logic

## Impact

- **Affected code**: `pdf_processor/` module
- **No breaking changes**: Existing CLI interface unchanged
- **Database**: No schema changes
- **Dependencies**: Add `pdfplumber` for table extraction

## Success Criteria

- Process Amex yearly statements that currently fail
- Process Chase statements that currently fail
- Maintain 100% success rate on Citi (already works)
- No regression on working PDFs
