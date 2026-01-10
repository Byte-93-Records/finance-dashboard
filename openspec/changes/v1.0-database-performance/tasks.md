# Tasks: Database Performance

## 1. Create Indexes (Alembic migration)
- [ ] 1.1 Create index: `transactions(transaction_date)`
- [ ] 1.2 Create index: `transactions(account_id)`
- [ ] 1.3 Create index: `transactions(transaction_hash)`
- [ ] 1.4 Create composite index: `transactions(account_id, transaction_date)`
- [ ] 1.5 Create index on materialized views (daily_summary, monthly_summary)

## 2. Configure Connection Pooling
- [ ] 2.1 Update SQLAlchemy engine: pool_size=10, max_overflow=10
- [ ] 2.2 Test concurrent connections from Grafana + Python
- [ ] 2.3 Document pool configuration in code comments

## 3. Configure Query Caching (Grafana)
- [ ] 3.1 Update Grafana datasource: enable query caching
- [ ] 3.2 Set cache TTL: 5 minutes for summary tables
- [ ] 3.3 Verify cache working: check Grafana logs

## 4. Benchmark & Validate
- [ ] 4.1 Generate 100k test transactions
- [ ] 4.2 Run EXPLAIN ANALYZE on key queries before/after indexes
- [ ] 4.3 Verify all queries < 500ms
- [ ] 4.4 Test dashboard load time: should be < 2 seconds
- [ ] 4.5 Document performance improvements in notes

## 5. Testing
- [ ] 5.1 Test index creation doesn't break existing queries
- [ ] 5.2 Test connection pool under load (simulate 20 concurrent requests)
- [ ] 5.3 Verify backward compatibility with existing code
