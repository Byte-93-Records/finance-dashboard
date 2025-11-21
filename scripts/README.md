# Finance Dashboard Scripts

## 📜 Available Scripts

### `process-and-view.sh` - Complete Pipeline

**What it does:**
1. ✅ Starts PostgreSQL and Grafana containers
2. ✅ Processes all PDFs in `data/pdfs/` to CSV (or skip if using direct CSV exports)
3. ✅ Ingests all CSVs to PostgreSQL database
4. ✅ Verifies data was loaded
5. ✅ Shows you how to access Grafana and database

**Usage:**
```bash
./scripts/process-and-view.sh
```

**Before running:**
- **Option 1:** Place PDF statements in `data/pdfs/` (auto-converts to CSV)
- **Option 2:** Place CSV exports directly in `data/csv/` (recommended for Amex)
- Make sure Docker is running
- Ensure `.env` file exists with proper credentials

**After running:**
- **Grafana:** http://localhost:3000
  - Username: `admin`
  - Password: Check `GF_SECURITY_ADMIN_PASSWORD` in `.env` (default: `grafana123`)
- **Database:** `docker compose exec postgres psql -U finance -d finance_db`

**Filename Format:**
Name files as: `{bank}_{card}_{month}_{year}.{pdf|csv}`
- Example: `citi_thankyou_01_2025.pdf`
- Example: `amex_bluecash_all_2024.csv`
- See `docs/filename-format.md` for details

---

## 🔧 Manual Steps (if needed)

If you want to run steps individually:

### Start services:
```bash
docker compose up -d postgres grafana
```

### Process PDFs to CSV:
```bash
docker compose run --rm pdf-processor python -m pdf_processor.cli process
```

### Ingest CSV to database:
```bash
docker compose run --rm pdf-processor python ingest.py /data/csv/your_file.csv 1
```

### Stop services:
```bash
docker compose down
```

### View database:
```bash
docker compose exec postgres psql -U finance -d finance_db
```

---

## 📊 Quick Database Queries

**Count transactions:**
```sql
SELECT COUNT(*) FROM transactions;
```

**View recent transactions:**
```sql
SELECT transaction_date, description, amount 
FROM transactions 
ORDER BY transaction_date DESC 
LIMIT 10;
```

**Total spending:**
```sql
SELECT SUM(amount) 
FROM transactions 
WHERE amount > 0;
```
