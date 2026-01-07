# Proposal: Data Architecture for Scale

## Why

Current single-table schema won't scale to 100k+ transactions:
- Grafana queries all rows for every panel → slow dashboards
- No aggregate data available → expensive computations
- Single query point for multiple dashboard panels = bottleneck

Result: Dashboard will slow from milliseconds to seconds/minutes at scale.

## What Changes

Implement two-tier architecture: **Raw Layer** (immutable archive) + **Analytics Layer** (fast queries).

```
┌────────────────────────────────┐
│ Raw Layer (Archive)            │
├────────────────────────────────┤
│ transactions (partitioned)     │  ← All data, partitioned by year
│ import_logs                    │  ← Track what was imported when
└────────────────────────────────┘

┌────────────────────────────────┐
│ Analytics Layer (Grafana)      │
├────────────────────────────────┤
│ daily_summary                  │  ← Spending per day/account
│ monthly_summary                │  ← Spending per month/account/category
│ merchant_summary               │  ← Top merchants by spending
└────────────────────────────────┘
```

**New tables:**
- `daily_summary` - Materialized view: total spending by day & account
- `monthly_summary` - Materialized view: total spending by month, account, category
- `merchant_summary` - Materialized view: top 100 merchants & total spent
- `import_logs` - Track each import batch (file, count, timestamp)

**Schema changes:**
- Add `category` column to `transactions` (prepare for v0.3)
- Add `import_id` to `transactions` (link to import_logs)
- Partition `transactions` by year (separate tables: `transactions_2024`, `transactions_2025`, etc.)

## Impact

- **Raw data**: Unaffected, preserved for audit
- **Queries**: Grafana queries materialized views (~100ms max)
- **Dashboard**: O(1) query performance regardless of row count
- **Import time**: Slightly longer (must refresh views), but still < 5min for 100k rows

## Success Criteria

- Materialized views populated after each import
- Dashboard queries reference summary tables only
- 100k row import completes with view refresh in < 5 minutes
- Grafana dashboards load in < 2 seconds
- Raw transactions table preserved for drill-down/search

## Database Impact

**Requires:** PostgreSQL (already in stack)

**Dependencies:**
- SQLAlchemy (ORM for new models)
- Alembic (migration: create views, add columns, partition table)

See TOOLS.md for version requirements.
