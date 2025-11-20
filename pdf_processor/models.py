from decimal import Decimal
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class TransactionRow(BaseModel):
    """Represents a single transaction row extracted from a PDF."""
    transaction_date: date
    description: str
    amount: Decimal
    transaction_type: str = Field(..., description="Type of transaction: DEBIT or CREDIT")
    category: Optional[str] = None
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        return v.quantize(Decimal("0.01"))

class CSVOutput(BaseModel):
    """Represents the complete CSV output for a processed PDF."""
    source_file: str
    extraction_date: date
    transactions: List[TransactionRow]
    total_count: int
    total_amount: Decimal
