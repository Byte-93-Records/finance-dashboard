## What Problems Does Repository Pattern Solve?

### 1. **Testability Without Database**
```python
# WITHOUT Repository Pattern - Hard to test
def calculate_monthly_spending(session):
    transactions = session.query(Transaction)\
        .filter(Transaction.date >= start_date)\
        .filter(Transaction.amount < 0)\
        .all()
    return sum(t.amount for t in transactions)

# Test requires real database or complex SQLAlchemy mocking
```

```python
# WITH Repository Pattern - Easy to test
def calculate_monthly_spending(transaction_repo: TransactionRepository):
    transactions = transaction_repo.get_expenses_for_month(month, year)
    return sum(t.amount for t in transactions)

# Test with simple mock - no database needed!
class MockTransactionRepo(TransactionRepository):
    def get_expenses_for_month(self, month, year):
        return [Transaction(amount=-50.00), Transaction(amount=-100.00)]
```

**Problem Solved**: Tests run 100x faster, no Docker containers needed for unit tests.

---

### 2. **Business Logic Doesn't Know About Database**
```python
# WITHOUT Repository - Business logic coupled to SQLAlchemy
class TransactionService:
    def import_csv(self, csv_data, session):
        for row in csv_data:
            # Business logic mixed with database details
            existing = session.query(Transaction)\
                .filter_by(hash=calculate_hash(row))\
                .first()
            if not existing:
                session.add(Transaction(**row))
        session.commit()
```

```python
# WITH Repository - Clean separation
class TransactionService:
    def __init__(self, transaction_repo: TransactionRepository):
        self.repo = transaction_repo
    
    def import_csv(self, csv_data):
        for row in csv_data:
            # Pure business logic - no SQLAlchemy knowledge
            if not self.repo.exists_by_hash(calculate_hash(row)):
                self.repo.add(Transaction.from_csv(row))
        self.repo.save_all()
```

**Problem Solved**: If you switch from PostgreSQL to MongoDB later, only repositories change, not business logic.

---

### 3. **Query Reusability & Consistency**
```python
# WITHOUT Repository - Duplicate queries everywhere
# In ingestion/service.py
duplicates = session.query(Transaction)\
    .filter_by(account_id=account_id, hash=tx_hash)\
    .first()

# In reports/generator.py (same query, slightly different)
duplicates = session.query(Transaction)\
    .filter(Transaction.account_id == account_id)\
    .filter(Transaction.hash == tx_hash)\
    .first()
```

```python
# WITH Repository - Single source of truth
class TransactionRepository:
    def find_duplicate(self, account_id: int, tx_hash: str) -> Optional[Transaction]:
        """Find existing transaction by account and hash."""
        return self.session.query(Transaction)\
            .filter_by(account_id=account_id, hash=tx_hash)\
            .first()

# Used consistently everywhere
duplicate = transaction_repo.find_duplicate(account_id, tx_hash)
```

**Problem Solved**: Query logic lives in one place. Changes propagate automatically.

---

### 4. **Easier to Reason About Data Access**
```python
# WITHOUT Repository - Where do transactions come from?
def generate_report(session):
    # Is this all transactions? Filtered? From which account?
    transactions = session.query(Transaction).all()
    # ...
```

```python
# WITH Repository - Clear intent
class TransactionRepository:
    def get_all_for_account(self, account_id: int) -> List[Transaction]:
        """Get all transactions for specific account."""
        pass
    
    def get_expenses_in_range(self, start: date, end: date) -> List[Transaction]:
        """Get expense transactions within date range."""
        pass

# Usage is self-documenting
transactions = repo.get_all_for_account(account_id=123)
expenses = repo.get_expenses_in_range(start_date, end_date)
```

**Problem Solved**: Code reads like English. Intent is clear.

---

### 5. **Centralized Data Access Policies**
```python
# WITH Repository - Enforce rules in one place
class TransactionRepository:
    def get_transactions(self, filters: dict) -> List[Transaction]:
        query = self.session.query(Transaction)
        
        # Always exclude soft-deleted (enforced everywhere)
        query = query.filter(Transaction.deleted_at.is_(None))
        
        # Always order by date descending
        query = query.order_by(Transaction.date.desc())
        
        if filters.get('account_id'):
            query = query.filter_by(account_id=filters['account_id'])
        
        return query.all()
```

**Problem Solved**: You'll never accidentally show deleted transactions or forget to sort by date.

---

### 6. **Simplified Dependency Injection**
```python
# WITH Repository Pattern - Easy to inject dependencies
class IngestionService:
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        account_repo: AccountRepository,
        logger: Logger
    ):
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo
        self.logger = logger

# In tests
service = IngestionService(
    transaction_repo=MockTransactionRepo(),
    account_repo=MockAccountRepo(),
    logger=MockLogger()
)

# In production
service = IngestionService(
    transaction_repo=SQLAlchemyTransactionRepo(session),
    account_repo=SQLAlchemyAccountRepo(session),
    logger=StructlogLogger()
)
```

**Problem Solved**: Swap implementations easily (mocks for tests, real repos for production).

---

## Why Repository Pattern for **Your Finance Project** Specifically?

### Your Unique Requirements:
1. **Idempotent Imports** - Need `find_duplicate()` logic reused across CSV parser, PDF processor, manual import
2. **Test Coverage 80%** - Can't hit that without fast unit tests (repository mocking enables this)
3. **Multiple Data Sources** - PDFs → CSV → DB. Repository abstracts "where did this transaction come from?"
4. **Financial Correctness** - Centralized query logic reduces bugs (e.g., always filter deleted, always use Decimal)
5. **Future Grafana Views** - Repositories can expose data optimized for Grafana without business logic knowing

---

## Trade-Off: Boilerplate Code

**Yes, you write more code:**

```python
# Direct ORM (fewer lines)
session.query(Transaction).filter_by(account_id=123).all()

# Repository Pattern (more lines)
class TransactionRepository:
    def get_by_account(self, account_id: int) -> List[Transaction]:
        return self.session.query(Transaction).filter_by(account_id=account_id).all()

repo.get_by_account(123)
```

**But you gain:**
- ✅ **100x faster tests** (no database needed)
- ✅ **Clear interfaces** (what queries exist?)
- ✅ **Reusable queries** (no copy-paste)
- ✅ **Easy refactoring** (change query in one place)
- ✅ **Database abstraction** (could swap PostgreSQL for DuckDB later)

---

## Bottom Line

**Repository Pattern solves**: "How do I test business logic without spinning up PostgreSQL every time?"

For your finance dashboard:
- You need **80% test coverage** → Repositories enable fast unit tests
- You have **idempotent import logic** → Repositories centralize duplicate detection
- You want **maintainability** → Business logic doesn't know about SQLAlchemy

**Without repositories**: Every test needs Docker PostgreSQL container (30 seconds startup), business logic tightly coupled to database.

**With repositories**: Unit tests run in milliseconds, business logic tests read like specifications.

