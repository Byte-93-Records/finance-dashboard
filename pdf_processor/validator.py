import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from decimal import Decimal, InvalidOperation
from datetime import datetime

from .exceptions import ValidationError
from .models import TransactionRow

class CSVValidator:
    """Validates CSV files against the expected schema."""
    
    REQUIRED_COLUMNS = ["transaction_date", "description", "amount", "transaction_type"]
    
    def validate(self, csv_path: Path) -> bool:
        """
        Validate a CSV file.
        
        Args:
            csv_path: Path to the CSV file.
            
        Returns:
            True if valid, raises ValidationError otherwise.
        """
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            raise ValidationError(f"Failed to read CSV: {e}")
            
        self._validate_schema(df)
        self._validate_data(df)
        
        return True
    
    def _validate_schema(self, df: pd.DataFrame) -> None:
        """Validate that required columns exist."""
        missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            raise ValidationError(f"Missing required columns: {', '.join(missing_columns)}")
            
    def _validate_data(self, df: pd.DataFrame) -> None:
        """Validate data types and formats."""
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Validate date
                try:
                    pd.to_datetime(row['transaction_date'])
                except (ValueError, TypeError):
                    errors.append(f"Row {index + 1}: Invalid date format for 'transaction_date': {row['transaction_date']}")
                
                # Validate amount
                try:
                    amount = Decimal(str(row['amount']))
                    if amount.as_tuple().exponent < -2:
                         errors.append(f"Row {index + 1}: Amount has more than 2 decimal places: {row['amount']}")
                except (InvalidOperation, TypeError, ValueError):
                    errors.append(f"Row {index + 1}: Invalid amount format: {row['amount']}")
                
                # Validate transaction type
                if row['transaction_type'] not in ['DEBIT', 'CREDIT']:
                     errors.append(f"Row {index + 1}: Invalid transaction_type: {row['transaction_type']}. Must be DEBIT or CREDIT.")
                     
            except Exception as e:
                errors.append(f"Row {index + 1}: Unexpected error: {e}")
                
        if errors:
            raise ValidationError("\n".join(errors))
