# OpenSpec Redundancy Fix - Summary of Changes

## Overview
Fixed critical redundancy between `csv-parser-and-database` and `ingestion-orchestration` changes by removing duplicate `ingestion/` module references and properly separating concerns.

---

## Changes Made

### 1. csv-parser-and-database/proposal.md
**Removed**:
- "Ingestion Orchestration" section (lines 27-31)
- `ingestion/` from module list
- Orchestrator-related next steps

**Updated**:
- Module list: `csv_parser/`, `database/` (removed `ingestion/`)
- Dependencies: Added Pydantic
- Next steps: Removed "Build ingestion orchestrator"

### 2. csv-parser-and-database/design.md
**Removed**:
- `ingestion/` module structure (orchestrator.py, hasher.py, exceptions.py)
- `IngestionOrchestrator` class documentation
- Orchestration-related processing flow steps

**Updated**:
- Module structure: Moved `TransactionHasher` from `ingestion/hasher.py` to `csv_parser/hasher.py`
- Processing flow: Simplified to focus on CSV parsing and database loading
- Migration plan: Removed `ingestion/` from module creation and rollback

**Key Change**:
```diff
- ingestion/
- ├── orchestrator.py     # IngestionOrchestrator
- ├── hasher.py          # TransactionHasher
- └── exceptions.py

+ csv_parser/
+ ├── hasher.py           # TransactionHasher (moved here)
```

### 3. csv-parser-and-database/tasks.md
**Removed**:
- Section 6: "Ingestion Orchestration" (entire section)
- Section 7: "CLI Interface" (entire section)
- `ingestion/` from project setup

**Updated**:
- Section 1.1: Module directories changed from `csv_parser/`, `database/`, `ingestion/` to just `csv_parser/`, `database/`
- Section 5: Renamed to "Transaction Hashing" (removed "and Deduplication")
- Section 5.1: Changed path from `ingestion/hasher.py` to `csv_parser/hasher.py`
- Renumbered all subsequent sections (8→6, 9→7, 10→8, 11→9, 12→10)

**Result**: Reduced from 12 sections to 10 sections (~50 tasks removed)

### 4. ingestion-orchestration/proposal.md
**Added**:
- Dependency note: "This change depends on `csv-parser-and-database` for TransactionHasher"

### 5. ingestion-orchestration/design.md
**Updated**:
- Added comment in `IngestionOrchestrator.__init__`: "TransactionHasher imported from csv_parser.hasher"

---

## Module Ownership After Fix

| Module | Owner | Purpose |
|--------|-------|---------|
| `csv_parser/` | csv-parser-and-database | CSV parsing, validation, hashing |
| `database/` | csv-parser-and-database | SQLAlchemy models, repositories, migrations |
| `ingestion/` | ingestion-orchestration | ETL orchestration, CLI |

---

## Key Improvements

### ✅ Eliminated Redundancy
- **Before**: ~300 lines of duplicate content across two changes
- **After**: Zero duplication, clear separation of concerns

### ✅ Proper Module Placement
- **TransactionHasher**: Moved from `ingestion/hasher.py` to `csv_parser/hasher.py`
  - **Rationale**: Hashing is part of CSV processing/validation, not orchestration
  - **Usage**: Ingestion orchestrator imports from `csv_parser.hasher`

### ✅ Clear Dependencies
- `ingestion-orchestration` explicitly depends on `csv-parser-and-database`
- Dependency documented in proposal

### ✅ Lean Documentation
- Removed ~50 duplicate tasks from csv-parser-and-database
- Each change now focuses on its specific scope

---

## Files Modified

1. `/Users/jrk/Documents/Git/GitHub/finance-dashboard/openspec/changes/csv-parser-and-database/proposal.md`
2. `/Users/jrk/Documents/Git/GitHub/finance-dashboard/openspec/changes/csv-parser-and-database/design.md`
3. `/Users/jrk/Documents/Git/GitHub/finance-dashboard/openspec/changes/csv-parser-and-database/tasks.md`
4. `/Users/jrk/Documents/Git/GitHub/finance-dashboard/openspec/changes/ingestion-orchestration/proposal.md`
5. `/Users/jrk/Documents/Git/GitHub/finance-dashboard/openspec/changes/ingestion-orchestration/design.md`

---

## Verification

### Before Fix
- ❌ `csv-parser-and-database` included `ingestion/` module
- ❌ Duplicate orchestrator and CLI implementation tasks
- ❌ Unclear which change owns `ingestion/`

### After Fix
- ✅ `csv-parser-and-database` owns only `csv_parser/` and `database/`
- ✅ `ingestion-orchestration` owns only `ingestion/`
- ✅ TransactionHasher properly located in `csv_parser/hasher.py`
- ✅ Clear dependency: ingestion-orchestration → csv-parser-and-database
- ✅ No duplicate content

---

## Next Steps (Optional)

1. **Review grafana-dashboards**: Already verified clean, no changes needed
2. **Test OpenSpec validation**: Run `openspec validate` when CLI is installed
3. **Begin implementation**: Start with csv-parser-and-database, then ingestion-orchestration
