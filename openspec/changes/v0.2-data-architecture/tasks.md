# Tasks: Data Architecture for Scale

## 1. Database Schema Updates (Alembic migrations)
- [ ] 1.1 Create migration: add `category` column to transactions (VARCHAR, nullable)
- [ ] 1.2 Create migration: add `import_id` column and foreign key to transactions
- [ ] 1.3 Create migration: create `import_logs` table (id, timestamp, file_count, transaction_count, status)
- [ ] 1.4 Create migration: partition transactions table by year (2023, 2024, 2025)
- [ ] 1.5 Verify migrations work: test rollback and reapply

## 2. Create Raw Data Layer
- [ ] 2.1 Update `database/models.py`: add `ImportLog` SQLAlchemy model
- [ ] 2.2 Update `Transaction` model: add `category` and `import_id` fields
- [ ] 2.3 Backfill `import_id` for existing transactions (treat as single "initial" import)

## 3. Create Materialized Views (PostgreSQL)
- [ ] 3.1 Create `daily_summary` view: date, account_id, total spending
- [ ] 3.2 Create `monthly_summary` view: year, month, account_id, category, total spending
- [ ] 3.3 Create `merchant_summary` view: merchant name, total spending, transaction count
- [ ] 3.4 Create indexes on materialized views for fast queries

## 4. Implement View Refresh Logic
- [ ] 4.1 Create function: `refresh_materialized_views()` in database layer
- [ ] 4.2 Call refresh after each import completes
- [ ] 4.3 Test view refresh with 10k transactions
- [ ] 4.4 Benchmark: measure refresh time

## 5. Update Import Pipeline
- [ ] 5.1 Update `ingest.py`: log each import batch to `import_logs`
- [ ] 5.2 Update `ingest.py`: track `import_id` for each transaction
- [ ] 5.3 Implement deduplication check: skip files already in `import_logs`

## 6. Testing
- [ ] 6.1 Generate test data: 100k transactions across 3 accounts
- [ ] 6.2 Test import: runs in < 5 minutes with view refresh
- [ ] 6.3 Test view queries: all return in < 500ms
- [ ] 6.4 Test dashboard: loads in < 2 seconds with 100k rows
- [ ] 6.5 Verify backward compatibility: existing Grafana queries still work

## 7. Documentation
- [ ] 7.1 Update `docs/database-architecture.md` with schema diagrams
- [ ] 7.2 Document materialized view refresh strategy
- [ ] 7.3 Document how to add new summary views
