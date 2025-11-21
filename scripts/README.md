# Finance Dashboard Scripts

## 📜 Available Scripts

### `process-and-view.sh` - Complete Pipeline

**What it does:**
1. ✅ Starts PostgreSQL and Grafana containers
2. ✅ Processes all PDFs in `data/pdfs/` to CSV
3. ✅ Ingests all CSVs to PostgreSQL database
4. ✅ Verifies data was loaded
5. ✅ Shows you how to access Grafana and database

**Usage:**
```bash
./scripts/process-and-view.sh
```

**Before running:**
- Place your PDF bank statements in `data/pdfs/`
- Make sure Docker is running

**After running:**
- View dashboards at http://localhost:3000 (admin/admin)
- Check database: `docker compose exec postgres psql -U finance -d finance_db`

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
