# Delta for Visualization

## ADDED Requirements

### Requirement: Grafana Dashboard Provisioning
The system SHALL automatically provision Grafana dashboards and data sources on container startup.

#### Scenario: Initial Grafana startup
- **GIVEN** Grafana container starts for first time
- **WHEN** provisioning executes
- **THEN** PostgreSQL data source SHALL be automatically configured
- **AND** all 4 dashboards SHALL be automatically loaded
- **AND** no manual configuration SHALL be required

#### Scenario: Dashboard JSON version control
- **GIVEN** dashboard JSON files in `grafana/dashboards/`
- **WHEN** Grafana container restarts
- **THEN** dashboards SHALL be reloaded from JSON files
- **AND** manual dashboard edits in UI SHALL be lost (unless exported to JSON)

### Requirement: PostgreSQL Read-Only Access for Grafana
The system SHALL provide a dedicated read-only PostgreSQL user for Grafana queries.

#### Scenario: Read-only user permissions
- **GIVEN** Grafana connected with `grafana_readonly` user
- **WHEN** Grafana executes SELECT query
- **THEN** query SHALL succeed
- **AND** user SHALL have SELECT permission on all tables and views

#### Scenario: Write operation prevention
- **GIVEN** Grafana connected with `grafana_readonly` user
- **WHEN** Grafana attempts INSERT, UPDATE, or DELETE
- **THEN** operation SHALL fail with permission denied error
- **AND** no data SHALL be modified

### Requirement: Account Overview Dashboard
The system SHALL provide an Account Overview dashboard showing current balances and recent transactions.

#### Scenario: Current account balances display
- **GIVEN** 3 accounts with transactions
- **WHEN** Account Overview dashboard loads
- **THEN** dashboard SHALL display current balance for each account
- **AND** balances SHALL be from most recent transaction with balance field
- **AND** accounts with no balance data SHALL show "N/A"

#### Scenario: Recent transactions table
- **GIVEN** 100 transactions in last 30 days
- **WHEN** Account Overview dashboard loads
- **THEN** dashboard SHALL display table of recent transactions
- **AND** table SHALL be sorted by date descending (newest first)
- **AND** table SHALL include columns: date, account, description, amount, category

#### Scenario: Account filter variable
- **GIVEN** Account Overview dashboard with `$account` variable
- **WHEN** user selects specific account from dropdown
- **THEN** all panels SHALL filter to show only that account's data
- **AND** selecting "All" SHALL show data for all accounts

### Requirement: Spending Analysis Dashboard
The system SHALL provide a Spending Analysis dashboard showing spending trends and top merchants.

#### Scenario: Monthly spending by category chart
- **GIVEN** transactions across 6 months with categories assigned
- **WHEN** Spending Analysis dashboard loads
- **THEN** dashboard SHALL display bar chart of monthly spending by category
- **AND** chart SHALL use `v_monthly_spending_by_category` view
- **AND** chart SHALL be grouped by month and category

#### Scenario: Top merchants table
- **GIVEN** transactions from 50 different merchants
- **WHEN** Spending Analysis dashboard loads
- **THEN** dashboard SHALL display table of top 20 merchants by total spending
- **AND** table SHALL use `v_top_merchants` view
- **AND** table SHALL include columns: merchant, transaction count, total spent

#### Scenario: Date range filter
- **GIVEN** Spending Analysis dashboard with `$timeRange` variable
- **WHEN** user selects date range (e.g., "Last 3 months")
- **THEN** all panels SHALL filter to show only transactions in that range
- **AND** spending totals SHALL update accordingly

### Requirement: Income Tracking Dashboard
The system SHALL provide an Income Tracking dashboard showing income sources and trends.

#### Scenario: Monthly income trends chart
- **GIVEN** income transactions across 12 months
- **WHEN** Income Tracking dashboard loads
- **THEN** dashboard SHALL display time series chart of monthly income
- **AND** chart SHALL use `v_monthly_income` view
- **AND** chart SHALL show income trend line

#### Scenario: Total income stat panel
- **GIVEN** current month with income transactions
- **WHEN** Income Tracking dashboard loads
- **THEN** dashboard SHALL display stat panel with total income for current month
- **AND** stat SHALL update when month changes

### Requirement: Transaction Search Dashboard
The system SHALL provide a Transaction Search dashboard with filterable transaction list.

#### Scenario: Transaction table with all filters
- **GIVEN** 1000 transactions across multiple accounts and categories
- **WHEN** Transaction Search dashboard loads
- **THEN** dashboard SHALL display table of all transactions
- **AND** table SHALL support filtering by account, date range, category, and description
- **AND** table SHALL support sorting by any column

#### Scenario: Description text search
- **GIVEN** Transaction Search dashboard with `$description` variable
- **WHEN** user enters "STARBUCKS" in description search
- **THEN** table SHALL filter to show only transactions with "STARBUCKS" in description
- **AND** search SHALL be case-insensitive

#### Scenario: Multiple filter combination
- **GIVEN** Transaction Search dashboard
- **WHEN** user selects account="Chase Checking", date range="Last 30 days", category="Dining"
- **THEN** table SHALL show only transactions matching ALL filters
- **AND** transaction count SHALL update to reflect filtered results

### Requirement: PostgreSQL Views for Dashboard Queries
The system SHALL provide PostgreSQL views to optimize Grafana dashboard queries.

#### Scenario: Monthly spending by category view
- **GIVEN** `v_monthly_spending_by_category` view exists
- **WHEN** Grafana queries view for spending data
- **THEN** view SHALL return monthly spending grouped by category
- **AND** view SHALL only include debit transactions (expenses)
- **AND** view SHALL use SUM(ABS(amount)) for total spending

#### Scenario: Account balances view
- **GIVEN** `v_account_balances` view exists
- **WHEN** Grafana queries view for current balances
- **THEN** view SHALL return most recent balance per account
- **AND** view SHALL use DISTINCT ON (account_id) to get latest balance
- **AND** view SHALL include account name from accounts table

#### Scenario: Monthly income view
- **GIVEN** `v_monthly_income` view exists
- **WHEN** Grafana queries view for income data
- **THEN** view SHALL return monthly income totals
- **AND** view SHALL only include credit transactions (income)
- **AND** view SHALL group by month using DATE_TRUNC

#### Scenario: Top merchants view
- **GIVEN** `v_top_merchants` view exists
- **WHEN** Grafana queries view for merchant data
- **THEN** view SHALL return top 50 merchants by total spending
- **AND** view SHALL include transaction count and total spent per merchant
- **AND** view SHALL be sorted by total spent descending

### Requirement: Dashboard Responsive Design
The system SHALL provide dashboards that work on desktop and mobile browsers.

#### Scenario: Mobile browser access
- **GIVEN** Grafana dashboard accessed from mobile browser
- **WHEN** dashboard loads
- **THEN** dashboard panels SHALL resize to fit mobile screen
- **AND** dashboard SHALL be scrollable vertically
- **AND** all dashboard functionality SHALL work (filters, sorting, etc.)

### Requirement: Dashboard Auto-Refresh (Optional)
The system SHALL support optional auto-refresh of dashboards to show updated data.

#### Scenario: Manual refresh
- **GIVEN** dashboard with stale data
- **WHEN** user clicks refresh button
- **THEN** dashboard SHALL reload all panels with latest data from database

#### Scenario: Auto-refresh configuration
- **GIVEN** dashboard with auto-refresh enabled (e.g., 5 minutes)
- **WHEN** 5 minutes elapse
- **THEN** dashboard SHALL automatically refresh all panels
- **AND** user SHALL see updated data without manual refresh

### Requirement: Grafana Data Persistence
The system SHALL persist Grafana configuration and user preferences across container restarts.

#### Scenario: Container restart
- **GIVEN** Grafana container with user preferences (theme, favorites, etc.)
- **WHEN** container is stopped and restarted
- **THEN** user preferences SHALL be preserved
- **AND** dashboard edits SHALL be preserved (if saved to volume)
- **AND** data source configuration SHALL be preserved

### Requirement: Grafana Admin Access
The system SHALL provide admin access to Grafana for dashboard editing and configuration.

#### Scenario: Admin login
- **GIVEN** Grafana admin password configured in `.env`
- **WHEN** user navigates to http://localhost:3000
- **THEN** user SHALL be able to login with admin credentials
- **AND** admin SHALL have full dashboard editing permissions

#### Scenario: Anonymous viewer access
- **GIVEN** Grafana configured with anonymous access enabled
- **WHEN** unauthenticated user navigates to http://localhost:3000
- **THEN** user SHALL see dashboards in viewer mode (read-only)
- **AND** user SHALL NOT be able to edit dashboards
- **AND** user SHALL NOT need to login
