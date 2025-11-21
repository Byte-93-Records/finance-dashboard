from datetime import date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from .models import Account, Transaction, ImportLog

class AccountRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, account: Account) -> Account:
        self.session.add(account)
        self.session.commit()
        self.session.refresh(account)
        return account

    def get_by_id(self, id: int) -> Optional[Account]:
        return self.session.get(Account, id)

    def get_by_name(self, name: str) -> Optional[Account]:
        stmt = select(Account).where(Account.name == name)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_all(self) -> List[Account]:
        stmt = select(Account)
        return list(self.session.execute(stmt).scalars().all())

class TransactionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, transaction: Transaction) -> Transaction:
        self.session.add(transaction)
        self.session.commit()
        self.session.refresh(transaction)
        return transaction

    def bulk_create(self, transactions: List[Transaction]) -> int:
        self.session.add_all(transactions)
        self.session.commit()
        return len(transactions)

    def get_by_hash(self, hash: str) -> Optional[Transaction]:
        stmt = select(Transaction).where(Transaction.transaction_hash == hash)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_account(self, account_id: int, start_date: date, end_date: date) -> List[Transaction]:
        stmt = select(Transaction).where(
            Transaction.account_id == account_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        )
        return list(self.session.execute(stmt).scalars().all())

class ImportLogRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, log: ImportLog) -> ImportLog:
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log

    def get_by_file_hash(self, file_hash: str) -> Optional[ImportLog]:
        stmt = select(ImportLog).where(ImportLog.file_hash == file_hash)
        return self.session.execute(stmt).scalar_one_or_none()
