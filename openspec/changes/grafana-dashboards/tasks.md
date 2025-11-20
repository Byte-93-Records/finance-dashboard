# Tasks: Grafana Dashboards for Financial Visualization

## 1. Project Setup
- [ ] 1.1 Create `grafana/` directory structure
- [ ] 1.2 Create subdirectories: `dashboards/`, `provisioning/datasources/`, `provisioning/dashboards/`
- [ ] 1.3 Add Grafana environment variables to `.env`:
  - [ ] 1.3.1 `GRAFANA_ADMIN_PASSWORD=secure_admin_password`
  - [ ] 1.3.2 `GRAFANA_DB_PASSWORD=grafana_readonly_password`
- [ ] 1.4 Add Grafana service to `docker-compose.yml`
- [ ] 1.5 Configure volume mounts for dashboards and provisioning
- [ ] 1.6 Configure Grafana data volume for persistence

## 2. PostgreSQL Read-Only User
- [ ] 2.1 Create Alembic migration: `alembic revision -m "add grafana readonly user"`
- [ ] 2.2 Add SQL to create `grafana_readonly` user
- [ ] 2.3 Grant CONNECT, USAGE, SELECT permissions
- [ ] 2.4 Apply migration: `alembic upgrade head`
- [ ] 2.5 Verify user permissions: `psql -U grafana_readonly -d finance_db -c "\dt"`

## 3. PostgreSQL Views for Aggregations
- [ ] 3.1 Create Alembic migration: `alembic revision -m "add grafana views"`
- [ ] 3.2 Define `v_monthly_spending_by_category` view
- [ ] 3.3 Define `v_account_balances` view
- [ ] 3.4 Define `v_monthly_income` view
- [ ] 3.5 Define `v_top_merchants` view
- [ ] 3.6 Apply migration: `alembic upgrade head`
- [ ] 3.7 Verify views created: `SELECT * FROM v_account_balances;`
- [ ] 3.8 Test view performance with 1000+ transactions

## 4. Grafana Data Source Provisioning
- [ ] 4.1 Create `grafana/provisioning/datasources/postgresql.yml`
- [ ] 4.2 Configure PostgreSQL data source:
  - [ ] 4.2.1 Name: "Finance PostgreSQL"
  - [ ] 4.2.2 URL: postgres:5432
  - [ ] 4.2.3 Database: finance_db
  - [ ] 4.2.4 User: grafana_readonly
  - [ ] 4.2.5 Password from environment variable
- [ ] 4.3 Test data source connection after Grafana starts

## 5. Dashboard Creation - Account Overview
- [ ] 5.1 Start Grafana: `docker-compose up grafana`
- [ ] 5.2 Create "Account Overview" dashboard in UI
- [ ] 5.3 Add panel: Current balance per account (Stat panels)
- [ ] 5.4 Add panel: Account balance trends (Time series)
- [ ] 5.5 Add panel: Recent transactions table (last 30 days)
- [ ] 5.6 Add panel: Account distribution pie chart
- [ ] 5.7 Add dashboard variable: `$account` (account filter)
- [ ] 5.8 Export dashboard JSON
- [ ] 5.9 Save to `grafana/dashboards/account-overview.json`

## 6. Dashboard Creation - Spending Analysis
- [ ] 6.1 Create "Spending Analysis" dashboard in UI
- [ ] 6.2 Add panel: Monthly spending by category (Bar chart)
- [ ] 6.3 Add panel: Total spending trends (Time series)
- [ ] 6.4 Add panel: Top 20 merchants table
- [ ] 6.5 Add panel: Spending distribution by category (Pie chart)
- [ ] 6.6 Add dashboard variables: `$timeRange`, `$category`
- [ ] 6.7 Export dashboard JSON
- [ ] 6.8 Save to `grafana/dashboards/spending-analysis.json`

## 7. Dashboard Creation - Income Tracking
- [ ] 7.1 Create "Income Tracking" dashboard in UI
- [ ] 7.2 Add panel: Total income current month (Stat panel)
- [ ] 7.3 Add panel: Monthly income trends (Time series)
- [ ] 7.4 Add panel: Income by source (Bar chart)
- [ ] 7.5 Add panel: Year-over-year income comparison
- [ ] 7.6 Export dashboard JSON
- [ ] 7.7 Save to `grafana/dashboards/income-tracking.json`

## 8. Dashboard Creation - Transaction Search
- [ ] 8.1 Create "Transaction Search" dashboard in UI
- [ ] 8.2 Add panel: Transaction table with columns (date, account, description, amount, category)
- [ ] 8.3 Add dashboard variables:
  - [ ] 8.3.1 `$account` (account filter)
  - [ ] 8.3.2 `$timeRange` (date range picker)
  - [ ] 8.3.3 `$category` (category multi-select)
  - [ ] 8.3.4 `$description` (text search)
- [ ] 8.4 Configure table sorting (default: date descending)
- [ ] 8.5 Export dashboard JSON
- [ ] 8.6 Save to `grafana/dashboards/transaction-search.json`

## 9. Dashboard Provisioning Configuration
- [ ] 9.1 Create `grafana/provisioning/dashboards/default.yml`
- [ ] 9.2 Configure dashboard provider:
  - [ ] 9.2.1 Path: /etc/grafana/provisioning/dashboards/dashboards
  - [ ] 9.2.2 Type: file
  - [ ] 9.2.3 Options: foldersFromFilesStructure: true
- [ ] 9.3 Restart Grafana to test provisioning
- [ ] 9.4 Verify all 4 dashboards auto-loaded

## 10. Testing
- [ ] 10.1 Load sample transaction data (1000+ transactions, 3+ accounts)
- [ ] 10.2 Test Account Overview dashboard:
  - [ ] 10.2.1 Verify current balances display correctly
  - [ ] 10.2.2 Verify balance trends chart
  - [ ] 10.2.3 Verify recent transactions table
  - [ ] 10.2.4 Test account filter variable
- [ ] 10.3 Test Spending Analysis dashboard:
  - [ ] 10.3.1 Verify monthly spending chart
  - [ ] 10.3.2 Verify top merchants table
  - [ ] 10.3.3 Verify spending distribution pie chart
  - [ ] 10.3.4 Test date range and category filters
- [ ] 10.4 Test Income Tracking dashboard:
  - [ ] 10.4.1 Verify income totals
  - [ ] 10.4.2 Verify income trends chart
  - [ ] 10.4.3 Test date range filter
- [ ] 10.5 Test Transaction Search dashboard:
  - [ ] 10.5.1 Verify all transactions display
  - [ ] 10.5.2 Test account filter
  - [ ] 10.5.3 Test date range filter
  - [ ] 10.5.4 Test category filter
  - [ ] 10.5.5 Test description search
- [ ] 10.6 Test responsive design (mobile browser)
- [ ] 10.7 Verify read-only user cannot modify data

## 11. Documentation
- [ ] 11.1 Create `grafana/README.md` with dashboard documentation
- [ ] 11.2 Document how to export dashboard JSON
- [ ] 11.3 Document dashboard variables and filters
- [ ] 11.4 Add Grafana usage instructions to main `README.md`
- [ ] 11.5 Document Grafana admin password setup

## 12. Performance Optimization
- [ ] 12.1 Test view performance with 10,000+ transactions
- [ ] 12.2 Add indexes if queries are slow (transaction_date, account_id, category_id)
- [ ] 12.3 Run EXPLAIN ANALYZE on view queries
- [ ] 12.4 Consider materialized views if needed

## 13. Validation & Deployment
- [ ] 13.1 Verify Grafana service starts correctly
- [ ] 13.2 Verify data source connection works
- [ ] 13.3 Verify all dashboards load without errors
- [ ] 13.4 Test dashboard provisioning (delete container, restart, verify dashboards reload)
- [ ] 13.5 Verify Grafana data persists across container restarts
- [ ] 13.6 Create PR for review
- [ ] 13.7 Update `CHANGELOG.md` with feature addition
