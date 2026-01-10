# Tasks: Bulk Processing with Parallelization

## 1. Implement Worker Pool Architecture
- [ ] 1.1 Create `pdf_processor/bulk_processor.py` with ThreadPoolExecutor
- [ ] 1.2 Implement processor interface: `process_batch(pdf_dir, output_dir, num_workers=4)`
- [ ] 1.3 Create thread-safe queue for worker tasks
- [ ] 1.4 Test with 10 PDFs: verify all complete successfully

## 2. Implement Progress Tracking
- [ ] 2.1 Add progress bar using Click (click.progressbar)
- [ ] 2.2 Calculate and display ETA based on elapsed time
- [ ] 2.3 Log each PDF: filename, transaction count, extraction time
- [ ] 2.4 Log summary at end: total time, success count, failure count

## 3. Implement Resume from Failure
- [ ] 3.1 Update `ingest.py`: check `import_logs` before processing each PDF
- [ ] 3.2 Skip files already in `import_logs` (by filename/hash)
- [ ] 3.3 Allow retry of failed PDFs from `failed/` directory
- [ ] 3.4 Test: rerun same batch, verify no duplicates

## 4. Implement Memory-Efficient Streaming
- [ ] 4.1 Ensure PDFs not preloaded into memory (read one at a time)
- [ ] 4.2 Ensure CSVs not all held open (write as completed)
- [ ] 4.3 Monitor memory during 100-PDF test (should stay < 500MB)

## 5. Update CLI Interface
- [ ] 5.1 Update `cli.py`: add `--workers` flag (default 4)
- [ ] 5.2 Add `--skip-existing` flag to skip already-imported files
- [ ] 5.3 Add `--verbose` flag for detailed logging per PDF
- [ ] 5.4 Update help text with examples

## 6. Error Handling
- [ ] 6.1 Handle extraction failure: move PDF to `failed/`, log error
- [ ] 6.2 Handle database write failure: rollback transaction, log error
- [ ] 6.3 Handle worker crash: log, skip file, continue batch
- [ ] 6.4 Test batch with 1 failed PDF: verify others complete

## 7. Testing & Benchmarking
- [ ] 7.1 Test with 10 PDFs: measure speed vs single-threaded
- [ ] 7.2 Test with 100 PDFs: measure speed, memory, ETA accuracy
- [ ] 7.3 Test failure recovery: create 50-PDF batch, simulate crash at 30
- [ ] 7.4 Test no regressions: existing single-file processing still works
- [ ] 7.5 Benchmark target: 100 PDFs in < 2 minutes

## 8. Documentation
- [ ] 8.1 Document `--workers` flag and recommended values
- [ ] 8.2 Document resume workflow (moving failed PDFs back)
- [ ] 8.3 Document progress bar and ETA calculation
