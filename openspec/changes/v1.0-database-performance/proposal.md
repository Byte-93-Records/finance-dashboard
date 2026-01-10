# Proposal: Database Performance Optimization

## Why

At 100k+ transactions, queries are slow without proper indexes and partitioning:
- Dashboard waits for table scans across all rows
- Queries hit transaction_hash for deduplication on every import
- No connection pooling → connection overhead on each query

Result: Dashboard slow, imports slow, concurrent queries fail.

## What Changes

Add performance layer: **indexes, partitioning (via v1.0-data-architecture), and connection pooling**.

1. **Indexes**
   - `transaction_date` (date range queries in Grafana)
   - `account_id` (filter by account)
   - `transaction_hash` (deduplication lookups)
   - Composite: `(account_id, transaction_date)` (common Grafana queries)

2. **Partitioning** (handled by v1.0-data-architecture)
   - Split `transactions` by year
   - Queries automatically prune irrelevant partitions

3. **Connection Pooling**
   - Use SQLAlchemy connection pool
   - Grafana DataSource connection limit set

4. **Query Caching** (Grafana-level)
   - Cache summary table queries (1-5 min TTL)
   - Dashboard renders instantly on repeat views

## Impact

- **Import time**: -10% (faster dedup lookups)
- **Query time**: -80% (index scans vs table scans)
- **Dashboard load**: -90% (cached summary queries)
- **Memory**: Stable (partitioning helps)

## Success Criteria

- All queries complete in < 500ms
- Dashboard loads in < 2 seconds
- Index overhead < 20% of table size
- No query plan changes (verify with EXPLAIN)

## Tool References

See TOOLS.md:
- **SQLAlchemy** ≥2.0.0 (connection pooling)
- **Alembic** ≥1.13.0 (migration scripts)
- **PostgreSQL** 18 (indexes, partitioning)

## Dependencies

Requires completion of **v1.0-data-architecture** (partitioning).
