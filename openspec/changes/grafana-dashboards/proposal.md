# Proposal: Grafana Dashboards for Financial Visualization

## Why
The ETL pipeline (Extract → Transform → Load) will be complete after CSV parsing and database loading. Now we need visualization to make the financial data useful:
1. **Visualization Layer**: Create Grafana dashboards to visualize transaction data from PostgreSQL
2. **Financial Insights**: Provide spending analysis, income tracking, account balances, and trends
3. **Self-Service Analytics**: Enable users to explore their financial data without writing SQL

This completes the data pipeline: Extract (PDF → CSV) → Transform (CSV parsing) → Load (PostgreSQL) → **Visualize (Grafana)**.

## What Changes
### Grafana Dashboard Configuration (`grafana/`)
- Pre-built dashboards for common financial views:
  - **Account Overview**: Current balances, recent transactions, account summaries
  - **Spending Analysis**: Monthly spending by category, top merchants, spending trends
  - **Income Tracking**: Income sources, monthly income trends, year-over-year comparison
  - **Transaction Search**: Filterable transaction list with date range, amount, description search
- Dashboard JSON definitions for version control
- PostgreSQL data source configuration
- Read-only database user for Grafana (security boundary)

### PostgreSQL Views (`database/views/`)
- SQL views for complex aggregations:
  - `v_monthly_spending_by_category` - Monthly spending grouped by category
  - `v_account_balances` - Current balance per account (latest transaction balance)
  - `v_monthly_income` - Monthly income totals
  - `v_top_merchants` - Top spending merchants by total amount
- Views created via Alembic migrations for version control

### Docker Compose Integration
- Add Grafana service to `docker-compose.yml`
- Configure Grafana data source (PostgreSQL connection)
- Mount dashboard JSON files for automatic provisioning
- Configure Grafana environment variables (admin password, anonymous access)

## Impact
- **Affected specs**: `visualization` (new), `database-schema` (add views)
- **Affected code**:
  - New directory: `grafana/` (dashboards, provisioning config)
  - Database migrations: Add PostgreSQL views
  - Docker Compose: Add Grafana service
- **External dependencies**: Grafana (official Docker image: grafana/grafana:latest)
- **Testing**: Manual verification of dashboards with sample data

## Next Steps
1. Create Grafana dashboard JSON definitions
2. Define PostgreSQL views for aggregations
3. Configure Grafana data source provisioning
4. Create Alembic migration for database views
5. Add Grafana service to Docker Compose
6. Test dashboards with sample transaction data
7. Document dashboard usage in user guide
