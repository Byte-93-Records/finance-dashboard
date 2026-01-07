# Spec: Database Performance

## ADDED Requirements

### Requirement: Query Indexes
The system SHALL use indexes to accelerate common queries.

#### Scenario: Date range query performance
- **GIVEN** 100k transactions in table
- **WHEN** Grafana queries transactions by date range (Jan 2025)
- **THEN** query uses index_scan, completes in < 100ms

#### Scenario: Account filter query
- **GIVEN** 100k transactions from 5 accounts
- **WHEN** querying by account_id
- **THEN** uses index, completes in < 50ms

#### Scenario: Deduplication lookup performance
- **GIVEN** importing 1000 new transactions
- **WHEN** checking for duplicates via transaction_hash
- **THEN** hash lookups use index, completes in < 5ms total

---

### Requirement: Connection Pooling
The system SHALL reuse database connections for performance.

#### Scenario: Connection pool active
- **GIVEN** Grafana and Python import running concurrently
- **WHEN** both need database connections
- **THEN** connections come from pool (no new connection overhead)

#### Scenario: Pool exhaustion prevention
- **GIVEN** max_overflow=10 configured
- **WHEN** more than 10 concurrent requests
- **THEN** excess requests queue (no error)

---

### Requirement: Query Caching
The system SHALL cache summary table queries to avoid repeated computation.

#### Scenario: Dashboard panel caching
- **GIVEN** Grafana dashboard loaded
- **WHEN** user refreshes dashboard
- **THEN** summary queries use cache (< 1ms), no database query

#### Scenario: Cache TTL expiration
- **GIVEN** cache TTL set to 5 minutes
- **WHEN** 5+ minutes elapse
- **THEN** cache expires, next query hits database
