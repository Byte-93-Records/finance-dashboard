# Troubleshooting Guide

## Common Errors and Resolutions

### 1. "No tables found in PDF"
**Symptoms**: PDF moves to `data/failed/` and log contains `ExtractionError: No tables found`.
**Cause**: The PDF might be a scanned image or has a layout that Docling cannot parse as a table.
**Resolution**:
- Ensure the PDF is text-based (selectable text).
- Check if the statement format is supported (standard bank/brokerage layout).
- If it's a supported bank, please open an issue with the PDF sample (redacted).

### 2. "Processing timed out"
**Symptoms**: Log contains `ExtractionError: Processing timed out after 30s`.
**Cause**: The PDF is too large or complex to process within the default timeout.
**Resolution**:
- Increase `PDF_TIMEOUT_SECONDS` in your `.env` file (e.g., set to `60` or `120`).
- Split the PDF into smaller files if it contains many pages.

### 3. "Missing required columns"
**Symptoms**: Log contains `ValidationError: Missing required columns: ...`.
**Cause**: The extractor found a table, but it doesn't look like a transaction list (missing date, description, or amount).
**Resolution**:
- The extractor might have picked up a summary table instead of the transaction detail table.
- Currently, the system concatenates all tables. Improvements to table filtering are planned.

### 4. Docker Volume Issues
**Symptoms**: "Path does not exist" or files not appearing in `data/`.
**Cause**: Docker volume mounts might be misconfigured.
**Resolution**:
- Ensure you are running `docker compose` from the project root.
- Verify `docker-compose.yml` has the correct `./data:/data` mapping.
