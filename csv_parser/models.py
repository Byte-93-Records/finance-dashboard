from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, field_validator

class TransactionRow(BaseModel):
    transaction_date: date
    posting_date: date | None = None
    description: str
    amount: Decimal
    balance: Decimal | None = None
    transaction_type: Literal["debit", "credit"]

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        return v.quantize(Decimal("0.01"))
