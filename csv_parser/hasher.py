import hashlib
from datetime import date
from decimal import Decimal

class TransactionHasher:
    @staticmethod
    def hash_transaction(account_id: int, date: date, amount: Decimal, description: str) -> str:
        # Normalize description
        norm_desc = " ".join(description.lower().split())
        
        # Create raw string
        raw = f"{account_id}|{date.isoformat()}|{amount}|{norm_desc}"
        
        # Generate SHA-256 hash
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
