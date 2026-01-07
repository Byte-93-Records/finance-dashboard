# Proposal: Dashboard Improvements

## Why

Current dashboard is basic:
- No account filtering (all accounts in one graph = confusing)
- No date range selection (always shows entire history)
- Queries raw 100k rows per panel (slow)
- Transaction list has no pagination

Result: Dashboard is slow, hard to use, and doesn't support the data volume.

## What Changes

Redesign dashboard to filter, aggregate, and search efficiently:

1. **Dynamic Filters**
   - Account dropdown (query `accounts` table)
   - Date range preset buttons: Last 30 Days, Last Quarter, YTD, Custom
   - Filter state persists across dashboard refresh

2. **Query Optimization**
   - Spending trends panel → queries `monthly_summary` (not raw transactions)
   - Top merchants panel → queries `merchant_summary` (not raw transactions)
   - Daily heatmap → queries `daily_summary` (not raw transactions)
   - Transaction search → queries raw `transactions` with pagination (show 50 at a time)

3. **New Panels**
   - Account balance trend (per account, per month)
   - Category breakdown (if category data available)
   - Spending comparison YoY

## Impact

- **Dashboard load time**: 10s → < 2s
- **Query latency**: 2-5s → 100-500ms
- **Usability**: Can now filter by account and date
- **Data**: Supports 100k+ transactions

## Success Criteria

- Dashboard loads in < 2 seconds
- Filters work (account, date range)
- All queries use summary tables (no raw table scans)
- Pagination works on transaction search
- No regressions on existing panels

## Tool References

See TOOLS.md:
- **Grafana** latest (dashboards, query caching)
- **PostgreSQL** 18 (summary tables, indexes)

## Dependencies

Requires completion of:
- **v0.2-data-architecture** (summary tables exist)
- **v0.2-database-performance** (indexes for fast queries)
