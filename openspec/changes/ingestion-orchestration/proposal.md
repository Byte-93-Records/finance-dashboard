# Proposal: Ingestion Orchestration

## Why
The ETL pipeline components are complete individually (PDF extraction, CSV parsing, database loading), but they need orchestration to work together as a cohesive system:
1. **End-to-End Workflow**: Coordinate all three ETL phases (Extract → Transform → Load)
2. **Error Handling**: Manage failures at each phase without corrupting data
3. **User Interface**: Provide CLI for users to trigger imports and view status
4. **Automation**: Support scheduled/automated processing (future enhancement)

This completes the ETL pipeline: Extract (PDF → CSV) → Transform (CSV parsing) → Load (PostgreSQL) → **Orchestrate (tie it all together)**.

## What Changes
### Ingestion Orchestrator (`ingestion/orchestrator.py`)
- Coordinate full ETL pipeline execution
- Scan `/data/pdfs/` for new PDFs
- Invoke PDF processor for extraction
- Invoke CSV parser for validation
- Invoke database loader for ingestion
- Handle errors at each phase (move failed files, log errors)
- Generate summary reports (X PDFs processed, Y transactions imported, Z errors)

### CLI Interface (`ingestion/cli.py`)
- Command: `finance-import process` - Process all pending PDFs
- Command: `finance-import status` - Show import statistics
- Command: `finance-import create-account` - Create new account
- Options: `--dry-run`, `--account-id`, `--verbose`
- Progress indicators for batch processing
- Colored output for success/failure messages

### Scheduler Integration (Optional for v1)
- APScheduler for automated processing
- Configurable schedule (e.g., daily at 2am)
- Email notifications on failures (future enhancement)

## Impact
- **Affected specs**: `etl-orchestration` (new), `etl-pipeline` (modify to reference orchestrator)
- **Affected code**:
  - New module: `ingestion/` (orchestrator, CLI)
  - Integration: Tie together `pdf_processor/`, `csv_parser/`, `database/`
  - Dependencies: Click (CLI), APScheduler (optional)
- **External dependencies**: None (uses existing modules)
- **Testing**: Integration tests for end-to-end PDF → database flow

## Next Steps
1. Design orchestrator architecture
2. Implement ETL coordination logic
3. Build CLI interface with Click
4. Add error handling and rollback
5. Create integration tests with sample PDFs
6. Add scheduling support (optional for v1)
7. Document CLI usage in README
