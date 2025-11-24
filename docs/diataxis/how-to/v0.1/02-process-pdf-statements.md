# How to Process PDF Statements

**Version:** v0.1  
**Type:** How-To Guide  
**Time:** 5 minutes per PDF

## Prerequisites

- Development environment set up ([Guide](01-setup-environment.md))
- PDF bank statements ready

## Supported Banks

- ✅ **Citi**: ThankYou, Double Cash, etc.
- ⚠️ **Amex**: CSV export recommended (PDF processing may timeout)
- 🔄 **Others**: Will attempt generic processing with Docling

## Steps

### 1. Name Your PDF File

Format: `{bank}_{card}_{month}_{year}.pdf`

**Examples:**
```bash
citi_thankyou_01_2025.pdf        # Citi ThankYou, January 2025
citi_thankyou_02_2025.pdf        # Citi ThankYou, February 2025
chase_sapphire_03_2025.pdf       # Chase Sapphire, March 2025
```

For yearly statements, use `all`:
```bash
amex_bluecash_all_2024.pdf       # Amex Blue Cash, full year 2024
```

### 2. Place PDF in Input Directory

```bash
cp ~/Downloads/statement.pdf data/pdfs/citi_thankyou_01_2025.pdf
```

### 3. Run PDF Processor

```bash
docker compose run --rm pdf-processor python -m pdf_processor.cli process
```

**What happens:**
1. PDF is converted to CSV using Docling
2. CSV is validated (warnings only, won't fail)
3. PDF is moved to `data/processed/`
4. CSV is saved to `data/csv/`

### 4. Verify Output

Check CSV generated:
```bash
ls -lh data/csv/
head -20 data/csv/citi_thankyou_01_2025.csv
```

Expected format: Mixed columns with dates, descriptions, amounts

### 5. Check Processing Logs

If something went wrong:
```bash
# Check failed PDFs
ls data/failed/

# Read error log
cat data/failed/statement_name.error.log
```

## Common Issues

### PDF Processing Timeout

**Symptom:** Processing takes >5 minutes and fails

**Solution:**
```bash
# Increase timeout in .env
PDF_TIMEOUT_SECONDS=600  # 10 minutes

# Rebuild container
docker compose build pdf-processor

# Try again
docker compose run --rm pdf-processor python -m pdf_processor.cli process
```

### PDF Moved to Failed Directory

**Symptom:** PDF in `data/failed/` instead of `data/processed/`

**Solution:**
1. Check error log in same directory
2. If it's a complex PDF, try CSV export instead
3. Move PDF back to retry:
   ```bash
   mv data/failed/statement.pdf data/pdfs/
   ```

### CSV Looks Messy

**Don't worry!** The ingestion script uses heuristic parsing:
- Finds dates by pattern matching
- Finds amounts by looking for $ or decimals
- Finds descriptions as longest text

Just proceed to [How to Ingest CSV Data](03-ingest-csv-data.md)

## Alternative: Use CSV Export

For Amex or other problematic PDFs:

1. Log in to bank website
2. Download transactions as CSV
3. Name file: `{bank}_{card}_{month}_{year}.csv`
4. Place in `data/csv/` (skip PDF processing)
5. Go directly to [How to Ingest CSV Data](03-ingest-csv-data.md)

## Batch Processing

Process all PDFs at once:
```bash
# Copy all PDFs
cp ~/Downloads/*.pdf data/pdfs/

# Run processor (processes all PDFs in directory)
docker compose run --rm pdf-processor python -m pdf_processor.cli process

# Or use the automation script
./scripts/process-and-view.sh
```

## Next Steps

- [How to Ingest CSV Data](03-ingest-csv-data.md)
- [Troubleshoot PDF Extraction](../../explanation/v0.1/pdf-extraction-challenges.md)

---

**Related:**
- [Filename Format Reference](../../reference/v0.1/filename-format.md)
- [CSV Format Reference](../../reference/v0.1/csv-format.md)
