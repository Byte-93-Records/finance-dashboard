# Design: Grafana Dashboards for Financial Visualization

## Context

The finance dashboard ETL pipeline will have completed Extract (PDF → CSV), Transform (CSV parsing), and Load (PostgreSQL) phases. This design addresses the **Visualization** layer to make financial data accessible and actionable through Grafana dashboards.

**Current State:**
- Financial transactions stored in PostgreSQL database
- Normalized schema: `accounts`, `transactions`, `categories`, `import_logs`
- Data ready for querying and visualization

**Constraints:**
- **Read-Only Access**: Grafana uses read-only PostgreSQL user (no data modification)
- **Self-Hosted**: Grafana runs in Docker alongside PostgreSQL (no cloud services)
- **Version Control**: Dashboard JSON definitions stored in Git
- **Zero Frontend Code**: Use Grafana's built-in panels (no custom React/Vue components)
- **Privacy-First**: All data remains local (no external data sources)

**Stakeholders:**
- **End User**: Expects intuitive dashboards for spending analysis, income tracking, and transaction search
- **Database**: PostgreSQL provides data via views optimized for Grafana queries

## Goals / Non-Goals

**Goals:**
1. Create pre-built Grafana dashboards for common financial views
2. Define PostgreSQL views for complex aggregations (monthly spending, account balances)
3. Configure Grafana data source provisioning (automatic PostgreSQL connection)
4. Enable dashboard JSON version control for reproducibility
5. Provide read-only database access for security
6. Support responsive design (desktop and mobile)

**Non-Goals:**
- Real-time data updates (batch processing sufficient, manual dashboard refresh)
- Custom Grafana plugins (use built-in panels only)
- Multi-user authentication (single-user application)
- Alerting/notifications (focus on visualization only)
- Data export from Grafana (use PostgreSQL directly if needed)
- Mobile app (Grafana web UI responsive enough)

## Decisions

### Decision 1: Pre-Built Dashboard Approach
**Choice:** Create 4 core dashboards as JSON files, version-controlled in Git

**Dashboards:**
1. **Account Overview** - Current balances, recent transactions, account summaries
2. **Spending Analysis** - Monthly spending by category, top merchants, trends
3. **Income Tracking** - Income sources, monthly trends, year-over-year comparison
4. **Transaction Search** - Filterable transaction list with search

**Rationale:**
- **Reproducibility**: JSON definitions in Git enable easy restoration
- **Consistency**: All users get same dashboards (no manual setup)
- **Version Control**: Dashboard changes tracked like code
- **Provisioning**: Grafana auto-loads dashboards on startup

**Alternatives Considered:**
1. **Manual Dashboard Creation**: Users build own dashboards (inconsistent, no version control)
2. **Dashboard API**: Programmatically create dashboards (unnecessary complexity)
3. **Grafana Terraform Provider**: Infrastructure-as-code (overkill for 4 dashboards)

**Why Pre-Built JSON Wins:** Simplest approach for small number of dashboards, easy to maintain, works with Grafana provisioning.

### Decision 2: PostgreSQL Views for Aggregations
**Choice:** Create SQL views via Alembic migrations for complex queries

**Views to Create:**
```sql
-- Monthly spending by category
CREATE VIEW v_monthly_spending_by_category AS
SELECT 
    DATE_TRUNC('month', transaction_date) AS month,
    c.name AS category,
    SUM(ABS(amount)) AS total_spending
FROM transactions t
LEFT JOIN categories c ON t.category_id = c.id
WHERE transaction_type = 'debit'
GROUP BY month, c.name;

-- Current account balances (latest balance per account)
CREATE VIEW v_account_balances AS
SELECT DISTINCT ON (account_id)
    account_id,
    a.name AS account_name,
    balance,
    transaction_date
FROM transactions t
JOIN accounts a ON t.account_id = a.id
WHERE balance IS NOT NULL
ORDER BY account_id, transaction_date DESC;

-- Monthly income totals
CREATE VIEW v_monthly_income AS
SELECT 
    DATE_TRUNC('month', transaction_date) AS month,
    SUM(amount) AS total_income
FROM transactions
WHERE transaction_type = 'credit'
GROUP BY month;

-- Top merchants by spending
CREATE VIEW v_top_merchants AS
SELECT 
    description,
    COUNT(*) AS transaction_count,
    SUM(ABS(amount)) AS total_spent
FROM transactions
WHERE transaction_type = 'debit'
GROUP BY description
ORDER BY total_spent DESC
LIMIT 50;
```

**Rationale:**
- **Performance**: Pre-aggregated data faster than Grafana aggregations
- **Reusability**: Views used across multiple dashboard panels
- **Maintainability**: SQL logic in database, not scattered across dashboards
- **Version Control**: Views created via Alembic migrations (tracked in Git)

**Alignment with Project Conventions:**
- Per `project.md` Database Access Strategy: "Database views for complex Grafana analytics may be created via Alembic migrations"

### Decision 3: Grafana Provisioning for Auto-Configuration
**Choice:** Use Grafana provisioning to auto-configure data source and dashboards

**Directory Structure:**
```
grafana/
├── dashboards/
│   ├── account-overview.json
│   ├── spending-analysis.json
│   ├── income-tracking.json
│   └── transaction-search.json
└── provisioning/
    ├── datasources/
    │   └── postgresql.yml
    └── dashboards/
        └── default.yml
```

**Provisioning Config (`postgresql.yml`):**
```yaml
apiVersion: 1
datasources:
  - name: Finance PostgreSQL
    type: postgres
    url: postgres:5432
    database: finance_db
    user: grafana_readonly
    secureJsonData:
      password: ${GRAFANA_DB_PASSWORD}
    jsonData:
      sslmode: disable
      postgresVersion: 1800
```

**Rationale:**
- **Zero Manual Setup**: Grafana starts with data source and dashboards configured
- **Reproducibility**: New deployments automatically configured
- **Environment Variables**: Passwords injected via `.env` (not hardcoded)

### Decision 4: Read-Only Database User for Grafana
**Choice:** Create dedicated PostgreSQL user with SELECT-only permissions

**SQL:**
```sql
CREATE USER grafana_readonly WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE finance_db TO grafana_readonly;
GRANT USAGE ON SCHEMA public TO grafana_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafana_readonly;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO grafana_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO grafana_readonly;
```

**Rationale:**
- **Security Boundary**: Grafana cannot modify financial data
- **Principle of Least Privilege**: Only SELECT permissions granted
- **Audit Trail**: Separate user for Grafana queries (vs application user)

### Decision 5: Dashboard Panel Selection
**Choice:** Use Grafana built-in panels (no custom plugins)

**Panel Types:**
- **Time Series**: Spending/income trends over time
- **Bar Chart**: Monthly spending by category
- **Table**: Transaction list with sorting/filtering
- **Stat**: Current account balances, total spending
- **Pie Chart**: Spending distribution by category

**Rationale:**
- **Zero Custom Code**: No JavaScript/React development needed
- **Battle-Tested**: Built-in panels are production-grade
- **Responsive**: Built-in panels work on mobile
- **Maintenance**: No plugin updates to manage

**Alignment with Project Conventions:**
- Per `project.md` Visualization Strategy: "Use built-in panels only if built-in panels insufficient" (they are sufficient)

### Decision 6: Dashboard Variables for Filtering
**Choice:** Use Grafana variables for dynamic filtering (account, date range, category)

**Variables:**
- `$account` - Dropdown of all accounts
- `$timeRange` - Date range picker (default: last 30 days)
- `$category` - Multi-select category filter

**Rationale:**
- **User Control**: Filter dashboards without editing queries
- **Reusability**: Same dashboard shows different accounts/time periods
- **Performance**: Variables passed as SQL parameters (indexed queries)

## Implementation Architecture

### Directory Structure
```
grafana/
├── dashboards/
│   ├── account-overview.json       # Current balances, recent transactions
│   ├── spending-analysis.json      # Monthly spending, top merchants
│   ├── income-tracking.json        # Income sources, trends
│   └── transaction-search.json     # Filterable transaction list
├── provisioning/
│   ├── datasources/
│   │   └── postgresql.yml          # PostgreSQL data source config
│   └── dashboards/
│       └── default.yml             # Dashboard provisioning config
└── README.md                       # Dashboard documentation

database/migrations/versions/
└── xxx_add_grafana_views.py        # Alembic migration for views
```

### Dashboard Panels

**Account Overview Dashboard:**
- **Panel 1**: Stat panels showing current balance per account
- **Panel 2**: Time series of account balances over time
- **Panel 3**: Table of recent transactions (last 30 days)
- **Panel 4**: Pie chart of account distribution

**Spending Analysis Dashboard:**
- **Panel 1**: Bar chart of monthly spending by category
- **Panel 2**: Time series of total spending over time
- **Panel 3**: Table of top 20 merchants by spending
- **Panel 4**: Pie chart of spending distribution by category

**Income Tracking Dashboard:**
- **Panel 1**: Stat panel showing total income (current month)
- **Panel 2**: Time series of monthly income trends
- **Panel 3**: Bar chart of income by source (description)
- **Panel 4**: Year-over-year income comparison

**Transaction Search Dashboard:**
- **Panel 1**: Table of all transactions with filters:
  - Date range picker
  - Account dropdown
  - Category multi-select
  - Description text search
  - Amount range filter

### Docker Compose Configuration
```yaml
services:
  grafana:
    image: grafana/grafana:latest
    container_name: finance-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer
      - GRAFANA_DB_PASSWORD=${GRAFANA_DB_PASSWORD}
    volumes:
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards/dashboards:ro
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
      - grafana-data:/var/lib/grafana
    depends_on:
      - postgres
    networks:
      - finance-network

volumes:
  grafana-data:
```

## Risks / Trade-offs

### Risk 1: Dashboard JSON Drift
**Risk:** Manual dashboard edits in Grafana UI not saved to JSON files (lost on container restart)

**Mitigation:**
- Document dashboard export process in README
- Warn users: "Changes in UI are temporary unless exported to JSON"
- Consider read-only dashboard provisioning (prevent UI edits)
- Periodic dashboard export to Git (manual process)

**Likelihood:** Medium (users may forget to export)  
**Impact:** Low (can recreate dashboards from scratch)

### Risk 2: PostgreSQL View Performance
**Risk:** Complex views may be slow with large datasets (100,000+ transactions)

**Mitigation:**
- Test views with 100,000+ transaction fixtures
- Add indexes on view query columns (transaction_date, account_id, category_id)
- Use EXPLAIN ANALYZE to identify slow queries
- Consider materialized views if performance degrades (refresh on schedule)

**Likelihood:** Low (personal finance rarely exceeds 10,000 transactions)  
**Impact:** Medium (slow dashboards frustrating but not broken)

### Risk 3: Grafana Version Compatibility
**Risk:** Dashboard JSON may break with Grafana version upgrades

**Mitigation:**
- Pin Grafana version in `docker-compose.yml` (e.g., `grafana:10.2.0`)
- Test dashboard compatibility before upgrading Grafana
- Keep dashboard JSON simple (avoid experimental features)
- Document Grafana version in README

**Likelihood:** Low (Grafana maintains backward compatibility)  
**Impact:** Medium (dashboards may need manual fixes)

### Trade-off 1: No Real-Time Updates
**Accepted:** Dashboards require manual refresh to see new data

**Justification:**
- Batch ETL processing (not real-time ingestion)
- Manual refresh acceptable for personal finance use case
- Auto-refresh can be enabled in Grafana (e.g., every 5 minutes)
- Real-time updates add complexity (WebSockets, polling)

### Trade-off 2: Limited Customization vs Custom Web App
**Accepted:** Grafana's built-in panels may not support all desired visualizations

**Justification:**
- Built-in panels cover 90% of financial visualization needs
- Custom web app requires significant development effort (React, charting libraries, API)
- Grafana's limitations acceptable for personal use
- Can always build custom app later if needed (Grafana data source remains)

### Trade-off 3: Single-User Anonymous Access
**Accepted:** No multi-user authentication, anonymous viewer access enabled

**Justification:**
- Single-user application (per project constraints)
- Anonymous access simplifies setup (no login required)
- Grafana admin password still required for dashboard editing
- Network isolation provides security (Docker internal network)

## Migration Plan

**Initial Setup:**
1. Create `grafana/` directory structure
2. Add Grafana service to `docker-compose.yml`
3. Configure environment variables in `.env`:
   ```
   GRAFANA_ADMIN_PASSWORD=secure_admin_password
   GRAFANA_DB_PASSWORD=grafana_readonly_password
   ```
4. Create read-only PostgreSQL user via Alembic migration

**Database Views:**
1. Create Alembic migration: `alembic revision -m "add grafana views"`
2. Define SQL views in migration file
3. Apply migration: `alembic upgrade head`
4. Verify views: `SELECT * FROM v_account_balances;`

**Dashboard Creation:**
1. Start Grafana: `docker-compose up grafana`
2. Create dashboards in Grafana UI (http://localhost:3000)
3. Export dashboard JSON: Settings → JSON Model → Copy
4. Save JSON to `grafana/dashboards/`
5. Restart Grafana to test provisioning

**Testing Approach:**
1. Load sample transaction data (1000+ transactions across 3 accounts)
2. Verify each dashboard panel displays correctly
3. Test dashboard variables (account filter, date range, category filter)
4. Test responsive design (mobile browser)
5. Verify read-only user cannot modify data

**Rollback Plan:**
- Remove Grafana service from `docker-compose.yml`
- Drop PostgreSQL views: `alembic downgrade -1`
- Delete `grafana/` directory
- Remove Grafana environment variables from `.env`
- No data loss risk (visualization layer only)

## Open Questions

1. **Dashboard Refresh Rate**: Should dashboards auto-refresh? If so, how often?
   - **Recommendation**: Optional auto-refresh (default: off), user can enable 5-minute refresh

2. **Historical Data Retention**: Should we archive old transactions to improve query performance?
   - **Recommendation**: No archiving for v1 (keep all data), add archiving in v2 if needed

3. **Category Assignment UI**: Should Grafana include panels for assigning categories to transactions?
   - **Recommendation**: No, use separate admin tool or SQL for category assignment (Grafana read-only)

4. **Dashboard Sharing**: Should users be able to export/share dashboard snapshots?
   - **Recommendation**: Yes, enable Grafana snapshot feature (local snapshots, no external sharing)

5. **Custom Time Zones**: Should dashboards support multiple time zones?
   - **Recommendation**: No, assume local time zone (per project constraints)
