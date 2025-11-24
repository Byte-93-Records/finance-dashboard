# PDF Processor - Next Steps and Known Issues

## Current State

The PDF extraction system successfully extracts tables from financial statement PDFs using Docling. As of the latest implementation:

- ✅ **Basic extraction works**: PDFs are converted to CSV files
- ✅ **Timeout handling**: Configurable via `PDF_TIMEOUT_SECONDS` in `.env`
- ✅ **Error logging**: Full tracebacks are captured for debugging
- ⚠️ **Schema mapping**: Extracted columns are generic (0, 1, 2, 3) and don't match the expected transaction schema

## Known Issues

### 1. Processing Timeout

**Problem**: Large or complex PDFs may take longer than the default 30-second timeout.

**Symptoms**:
```
TimeoutError: PDF processing timed out
Pipeline StandardPdfPipeline failed
```

**Solution**:
- Increase `PDF_TIMEOUT_SECONDS` in `.env` (currently set to 120 seconds)
- For typical bank statements: 60-120 seconds is sufficient
- For large brokerage statements (>50 pages): consider 180-300 seconds

**Example**:
```bash
# In .env file
PDF_TIMEOUT_SECONDS=120  # or higher for complex PDFs
```

### 2. Schema Mismatch

**Problem**: Docling extracts raw table structures with generic column names (0, 1, 2, 3) instead of semantic names (date, description, amount).

**Why this happens**: Different banks format their PDFs differently. Some have:
- Column headers in the table
- Column headers outside the table (in header text)
- No explicit headers at all
- Multiple tables per page

**Current validation error**:
```
Missing required columns: transaction_date, description, amount, transaction_type
```

## Next Steps for Bank-Specific Support

### Option 1: Disable Strict Validation (Quick Fix)

**Pros**: Works immediately for any PDF
**Cons**: Downstream processing needs to handle variable schemas

**Implementation**:
1. Modify `pdf_processor/cli.py` to skip validation or make it optional
2. Add a `--skip-validation` flag
3. Save raw extracted CSVs as-is

### Option 2: Add Column Mapping Layer (Recommended)

**Pros**: Clean, standardized output; easier downstream processing
**Cons**: Requires bank-specific configuration

**Implementation approach**:

1. **Create bank detection logic** (`pdf_processor/bank_detector.py`):
   - Parse PDF metadata or text to identify the bank
   - Look for keywords like "Chase", "Bank of America", "Wells Fargo"
   
2. **Create bank-specific mappers** (`pdf_processor/mappers/`):
   ```python
   # mappers/chase.py
   class ChaseMapper:
       def map_columns(self, df: pd.DataFrame) -> pd.DataFrame:
           # Map Chase's column structure to standard schema
           return df.rename(columns={
               0: 'transaction_date',
               1: 'description',
               2: 'amount',
               # ... etc
           })
   ```

3. **Registry pattern**:
   ```python
   BANK_MAPPERS = {
       'chase': ChaseMapper(),
       'bofa': BankOfAmericaMapper(),
       'wells_fargo': WellsFargoMapper(),
       # ... etc
   }
   ```

4. **Update extraction flow**:
   ```
   PDF → Extract → Detect Bank → Map Columns → Validate → Save
   ```

### Option 3: LLM-Based Column Detection (Advanced)

**Pros**: Flexible, can handle unknown formats
**Cons**: Requires API access, costs money, slower

**Implementation**:
1. Extract first 5-10 rows of the CSV
2. Send to LLM with prompt: "Identify which columns represent date, description, amount, and type"
3. Apply the mapping
4. Cache mappings for future PDFs from the same bank

## Recommended Configuration by PDF Type

### Credit Card Statements
- **Timeout**: 60-90 seconds
- **Typical columns**: Date, Description, Amount
- **Challenge**: Payments vs charges often in same column with +/- signs

### Bank Statements  
- **Timeout**: 60-120 seconds
- **Typical columns**: Date, Description, Withdrawals, Deposits, Balance
- **Challenge**: Multiple columns for amount (debit/credit)

### Brokerage Statements
- **Timeout**: 120-300 seconds (often 20-50 pages)
- **Typical columns**: Trade Date, Settlement Date, Description, Symbol, Quantity, Price, Amount
- **Challenge**: Multiple table types (trades, dividends, fees, summary)

## Testing with New Banks

When adding support for a new bank's PDF format:

1. **Extract a sample**:
   ```bash
   docker compose run --rm pdf-processor python -m pdf_processor.cli process
   ```

2. **Inspect the raw CSV**:
   ```bash
   head -20 data/csv/[filename].csv
   ```

3. **Document the structure**:
   - What columns are present?
   - Which column is the date?
   - Which column is the description?
   - How is amount represented? (single column or debit/credit split?)
   - Are there transaction types?

4. **Create a mapper** (if using Option 2)

5. **Add tests** with anonymized sample PDF

## Performance Optimization

If processing many PDFs:

1. **Batch processing**: Process multiple PDFs in parallel (update `cli.py`)
2. **Disable OCR**: Already disabled in current config (`do_ocr=False` would be set if we weren't using defaults)
3. **Use faster table extraction**: Currently using default mode
4. **Cache processed PDFs**: Track by file hash to avoid reprocessing

## Code Locations

- Main extractor: `pdf_processor/extractor.py`
- CLI orchestration: `pdf_processor/cli.py`
- Validation: `pdf_processor/validator.py`
- Configuration: `.env` (PDF_TIMEOUT_SECONDS)
- Extracted CSVs: `data/csv/`
- Failed PDFs: `data/failed/` (with `.error.log` files)

## References

- Docling documentation: https://github.com/DS4SD/docling
- Current implementation uses default DocumentConverter() for maximum compatibility
- User's working reference script demonstrated this approach works reliably

## PDF Processing Learnings & Fixes (Implemented Nov 2025)

### Challenges Encountered
1. **Duplicate Columns**: Some PDFs contained tables with identical column headers (or no headers), causing `pd.concat` to crash with `InvalidIndexError`.
2. **Schema Mismatch**: Extracted CSVs lacked standard headers (`transaction_date`, `description`, `amount`), failing strict validation.
3. **Complex Layouts**: Multi-column layouts resulted in messy CSV structures that simple index-based parsing couldn't handle.

### Fixes Implemented
1. **Robust Column Deduplication**: Updated `pdf_processor/extractor.py` to automatically rename duplicate columns (e.g., `Column`, `Column.1`) to prevent crashes.
2. **Relaxed Validation**: Modified `pdf_processor/cli.py` to **warn** instead of **delete** files when validation fails, allowing "imperfect" CSVs to be ingested.
3. **Heuristic Ingestion**: Enhanced `ingest.py` with "smart parsing" logic:
   - **Date Detection**: Scans row for `MM/DD` or `MM/DD/YY` patterns.
   - **Amount Detection**: Looks for currency symbols (`$`) or decimal formats.
   - **Description Detection**: Identifies the longest text field as the description.

### Verification Results
- **Input**: 4 Citi ThankYou statements (Jan, Feb, Mar, May 2025)
- **Result**: All 4 processed successfully despite validation warnings.
- **Data**: 40 transactions ingested into PostgreSQL.
- **Grafana**: Data is now visible in the dashboard.
