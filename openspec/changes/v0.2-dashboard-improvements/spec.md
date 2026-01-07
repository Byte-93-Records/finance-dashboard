# Spec: Dashboard Improvements

## ADDED Requirements

### Requirement: Account Filtering
The dashboard SHALL filter data by selected account.

#### Scenario: Account dropdown selection
- **GIVEN** 3 accounts in database (Amex, Chase, Citi)
- **WHEN** user selects "Amex" in dropdown
- **THEN** all panels show only Amex transactions

#### Scenario: Filter persistence
- **GIVEN** account filter set to "Chase"
- **WHEN** dashboard is refreshed
- **THEN** filter remains "Chase" (state persisted in URL)

#### Scenario: All accounts option
- **GIVEN** user selects "All" in dropdown
- **WHEN** panels refresh
- **THEN** all accounts' data shown (default behavior)

---

### Requirement: Date Range Filtering
The dashboard SHALL allow selecting date ranges via presets or custom picker.

#### Scenario: Date preset buttons
- **GIVEN** dashboard loaded
- **WHEN** user clicks "Last 30 Days" button
- **THEN** all panels update to show only last 30 days

#### Scenario: Custom date range
- **GIVEN** custom date picker available
- **WHEN** user selects "2024-01-01" to "2024-12-31"
- **THEN** all panels filter to that year

#### Scenario: Filter persistence
- **GIVEN** date range set to "Last Quarter"
- **WHEN** dashboard refreshed
- **THEN** filter remains (state in URL)

---

### Requirement: Summary Table Queries
The dashboard panels SHALL query aggregated summary tables instead of raw transactions.

#### Scenario: Spending trend panel
- **GIVEN** 100k transactions in database
- **WHEN** spending trend panel loads
- **THEN** queries `monthly_summary`, completes in < 100ms

#### Scenario: Top merchants panel
- **GIVEN** 100k transactions from 1000+ merchants
- **WHEN** top merchants panel loads
- **THEN** queries `merchant_summary` (top 10), completes in < 50ms

#### Scenario: Daily heatmap
- **GIVEN** 100k transactions spread over 500 days
- **WHEN** daily heatmap renders
- **THEN** queries `daily_summary`, completes in < 100ms

---

### Requirement: Transaction Search with Pagination
The dashboard search panel SHALL query raw transactions with pagination.

#### Scenario: Paginated results
- **GIVEN** 100k transactions match search criteria
- **WHEN** user searches for "amazon"
- **THEN** displays first 50 results with "Next" button

#### Scenario: Search performance
- **GIVEN** search criteria entered
- **WHEN** executed
- **THEN** first page loads in < 500ms (uses index)

#### Scenario: Result navigation
- **GIVEN** on page 1 of search results
- **WHEN** user clicks page 3
- **THEN** database query uses OFFSET/LIMIT, completes in < 500ms

---

### Requirement: New Analytical Panels
The dashboard SHALL include enhanced analytical views.

#### Scenario: Account balance trend
- **GIVEN** monthly_summary with account_id
- **WHEN** account balance trend panel created
- **THEN** shows spending per account per month as line graph

#### Scenario: Dashboard load performance
- **GIVEN** all panels created and queries optimized
- **WHEN** dashboard loads
- **THEN** completes in < 2 seconds from cold cache
