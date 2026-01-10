# Proposal: Bulk Processing with Parallelization

## Why

Processing 100+ PDFs sequentially is slow:
- Each PDF takes 2-5 seconds to extract
- 100 PDFs = 200-500 seconds = 3-8 minutes
- Single-threaded, CPU bottleneck

Result: Users wait too long for large batches to complete.

## What Changes

Implement parallel PDF processing with worker pool:

1. **Parallel Extraction**
   - Use `concurrent.futures.ThreadPoolExecutor` (4-8 workers default)
   - Each worker processes a PDF independently
   - Shared database connection pool (already configured in v1.0-database-performance)

2. **Progress Tracking**
   - Real-time progress bar in CLI: `[████████░░] 80/100 PDFs (2 min remaining)`
   - Log each file: success, failure, extraction time

3. **Resume from Failure**
   - Track processed file hashes in `import_logs`
   - On retry: skip already-imported files
   - Partial batch failure doesn't require re-processing successful PDFs

4. **Memory Efficiency**
   - Stream PDFs (don't load all into memory)
   - Worker pool limits concurrent memory usage
   - Batched CSV writes (don't keep all CSVs open)

## Impact

- **Speed**: 3-8 min → ~1 min for 100 PDFs (8x worker improvement from parallelization overhead)
- **User experience**: See progress, know ETA
- **Reliability**: Easily retry failed imports without re-doing successful ones

## Success Criteria

- 100 PDFs process in < 2 minutes
- Progress bar shows accurate ETA
- Failed PDF doesn't block remaining files
- Retry skips already-processed files

## Tool References

See TOOLS.md:
- **Click** ≥8.0.0 (CLI with progress)
- **structlog** ≥24.0.0 (structured logging for each worker)
- **Python 3.11+** (concurrent.futures built-in)

## Dependencies

Depends on:
- **v1.0-pdf-processors** (stable extraction interface)
- **v1.0-database-performance** (connection pooling for concurrent writes)
