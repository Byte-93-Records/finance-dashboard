# Setting Up Grafana Dashboards

## Quick Start

### 1. Configure PostgreSQL Data Source

1. Open Grafana: http://localhost:3000
2. Login with `admin` / `admin`
3. Go to **Connections** → **Data sources** → **Add data source**
4. Select **PostgreSQL**
5. Configure:
   - **Name**: `Finance PostgreSQL`
   - **Host**: `postgres:5432`
   - **Database**: `finance_db`
   - **User**: `finance`
   - **Password**: `finance`
   - **TLS/SSL Mode**: `disable`
6. Click **Save & Test** - should see "Database Connection OK"

### 2. Import Dashboard

**Option A: Import via UI**
1. Go to **Dashboards** → **New** → **Import**
2. Click **Upload JSON file**
3. Select: `grafana/dashboards/finance_dashboard.json`
4. Select your **Finance PostgreSQL** datasource
5. Click **Import**

**Option B: Use Provisioning (Automatic)**
The dashboard should auto-load from `grafana/dashboards/finance_dashboard.json` when Grafana starts.

If it doesn't appear:
```bash
docker compose restart grafana
# Wait 30 seconds, then check Dashboards
```

## Dashboard Panels

The Finance Dashboard includes:

### 📊 Summary Stats (Top Row)
- **Total Spending** - Sum of all positive amounts (purchases)
- **Total Payments** - Sum of all negative amounts (payments made)
- **Transaction Count** - Total number of transactions

### 📋 Recent Transactions Table
- Last 100 transactions sorted by date
- Columns: Date, Description, Amount, Type
- Click column headers to sort

### 📈 Daily Spending Chart
- Bar chart showing spending per day
- Only shows purchases (positive amounts)
- Time-based visualization

## Creating Custom Panels

### Add a New Panel
1. Open the dashboard
2. Click **Add** → **Visualization**
3. Select **Finance PostgreSQL** datasource
4. Click **Code** (top right) to write SQL
5. Example query:
   ```sql
   SELECT 
     transaction_date as time,
     description,
     amount
   FROM transactions
   WHERE amount > 0
   ORDER BY transaction_date DESC
   LIMIT 20;
   ```
6. Click **Apply**

### Useful SQL Queries

**Top Merchants by Spending:**
```sql
SELECT 
  description,
  SUM(amount) as total_spent,
  COUNT(*) as transaction_count
FROM transactions
WHERE amount > 0
GROUP BY description
ORDER BY total_spent DESC
LIMIT 10;
```

**Monthly Spending:**
```sql
SELECT 
  DATE_TRUNC('month', transaction_date) as month,
  SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as spending,
  SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as payments
FROM transactions
GROUP BY month
ORDER BY month;
```

**Average Transaction Amount:**
```sql
SELECT 
  AVG(amount) as avg_transaction
FROM transactions
WHERE amount > 0;
```

## Troubleshooting

### "Database Connection failed"
- Ensure PostgreSQL is running: `docker compose ps postgres`
- Check host is `postgres:5432` (not `localhost`)
- Verify credentials: `finance` / `finance`

### "Dashboard not found"
- Restart Grafana: `docker compose restart grafana`
- Check file exists: `ls grafana/dashboards/`
- Import manually via UI

### "No data" on panels
- Verify data exists: 
  ```bash
  docker compose exec postgres psql -U finance -d finance_db -c "SELECT COUNT(*) FROM transactions;"
  ```
- Check date range (top-right corner) - expand to "Last 90 days"

### Panel shows error
- Click **Edit** on the panel
- Check the SQL query in **Query** tab
- Look for syntax errors
- Test query in psql first

## Next Steps

1. **Add Filters**: Create template variables for account filtering
2. **Add Alerts**: Set up alerts for unusual spending
3. **Export/Share**: Share dashboards with team members
4. **Customize**: Modify colors, thresholds, and layouts

## Tips

- 💡 Use **Time range** selector (top-right) to filter data
- 💡 Click panel titles to edit
- 💡 Save changes with **Ctrl+S** or **Save dashboard** button
- 💡 Create dashboard snapshots for sharing
- 💡 Use variables like `$__timeFilter(transaction_date)` for time-based queries
