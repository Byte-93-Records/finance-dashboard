# Spec: Bulk Processing with Parallelization

## ADDED Requirements

### Requirement: Parallel PDF Processing
The system SHALL extract multiple PDFs concurrently using a worker pool.

#### Scenario: 4-worker processing
- **GIVEN** 100 PDFs in input directory
- **WHEN** bulk processor runs with 4 workers
- **THEN** 4 PDFs extracted concurrently, others queue for available workers

#### Scenario: Worker count configuration
- **GIVEN** CLI invoked with `--workers 8`
- **WHEN** bulk processor starts
- **THEN** 8 worker threads spawned

#### Scenario: Memory-efficient streaming
- **GIVEN** bulk processing 100 PDFs
- **WHEN** monitor memory during processing
- **THEN** memory stays < 500MB (only active workers loaded)

---

### Requirement: Progress Tracking
The system SHALL display real-time progress to the user.

#### Scenario: Progress bar display
- **GIVEN** bulk processing started
- **WHEN** 3 PDFs complete out of 10
- **THEN** CLI shows `[███░░░░░░░░] 3/10 (ETA: 2m 30s)`

#### Scenario: Per-file logging
- **GIVEN** a PDF extracted successfully
- **WHEN** processing completes
- **THEN** logs: `amex_2025_01.pdf: 342 transactions extracted in 2.1s`

#### Scenario: Failure logging
- **GIVEN** a PDF fails extraction
- **WHEN** error occurs
- **THEN** logs: `chase_2025_01.pdf: ERROR - no transactions found (moved to failed/)`

---

### Requirement: Resume from Failure
The system SHALL allow retrying failed PDFs without re-processing successful ones.

#### Scenario: Skip already-imported files
- **GIVEN** previous import had 100 successful PDFs
- **WHEN** running import again with same 100 + 10 new PDFs
- **THEN** 100 PDFs skipped (checked via import_logs), only 10 new extracted

#### Scenario: Retry failed PDFs
- **GIVEN** previous import had 5 failed PDFs in `failed/` directory
- **WHEN** user moves them back to input and retries
- **THEN** only those 5 PDFs processed (others still recognized as done)

#### Scenario: Partial batch recovery
- **GIVEN** batch of 50 PDFs, import crashes after 30
- **WHEN** user retries same batch
- **THEN** only remaining 20 PDFs processed, no duplicates

---

### Requirement: Batch Completion
The system SHALL confirm successful batch completion with summary.

#### Scenario: Batch summary
- **GIVEN** bulk processing completes
- **WHEN** finished
- **THEN** displays: `✓ 100 PDFs processed | 34,287 transactions imported | 0 failed | 3m 45s elapsed`
