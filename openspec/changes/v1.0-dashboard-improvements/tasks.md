# Tasks: Dashboard Improvements

## 1. Create Filter Controls
- [ ] 1.1 Create account dropdown variable in Grafana
- [ ] 1.2 Create date range selector (preset buttons + custom picker)
- [ ] 1.3 Implement filter state persistence in URL parameters
- [ ] 1.4 Test filter combinations: account + date range

## 2. Update Panels to Use Summary Tables
- [ ] 2.1 Update Spending Trend panel: query `monthly_summary` instead of raw transactions
- [ ] 2.2 Update Top Merchants panel: query `merchant_summary`
- [ ] 2.3 Update Daily Heatmap: query `daily_summary`
- [ ] 2.4 Verify all queries include account and date filters
- [ ] 2.5 Verify all queries complete in < 500ms

## 3. Implement Transaction Search Panel
- [ ] 3.1 Create search input variable in Grafana
- [ ] 3.2 Create transactions panel: query `transactions` with pagination
- [ ] 3.3 Use LIMIT 50 and OFFSET for pagination
- [ ] 3.4 Add "Next/Previous" buttons for page navigation
- [ ] 3.5 Verify search uses transaction_date index for performance

## 4. Create New Analytical Panels
- [ ] 4.1 Create Account Balance Trend panel (line chart, by account & month)
- [ ] 4.2 Create Category Breakdown panel (pie chart, if categories available)
- [ ] 4.3 Create YoY Comparison panel (showing 2024 vs 2025)
- [ ] 4.4 Test all new panels with 100k test data

## 5. Test and Optimize
- [ ] 5.1 Load test dashboard with 100k transactions: measure load time
- [ ] 5.2 Verify all queries complete in < 500ms
- [ ] 5.3 Test all filter combinations (10 account × 5 date ranges = 50 combos)
- [ ] 5.4 Test pagination with various result sizes
- [ ] 5.5 Benchmark before/after: measure dashboard load time improvement

## 6. Documentation
- [ ] 6.1 Document filter usage in dashboard README
- [ ] 6.2 Document how to add new panels using summary tables
- [ ] 6.3 Add dashboard screenshots to docs/
- [ ] 6.4 Document query optimization approach (summary vs raw tables)

## 7. Verification
- [ ] 7.1 Verify no regressions: existing Grafana queries still work
- [ ] 7.2 Verify backward compatibility: can view pre-filter dashboards
- [ ] 7.3 Test with real data: 2024 credit card statements
