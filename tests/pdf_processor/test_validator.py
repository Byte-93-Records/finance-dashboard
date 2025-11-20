import pytest
import pandas as pd
from pathlib import Path
from pdf_processor.validator import CSVValidator
from pdf_processor.exceptions import ValidationError

@pytest.fixture
def validator():
    return CSVValidator()

def test_validate_valid_csv(validator, tmp_path):
    csv_path = tmp_path / "valid.csv"
    df = pd.DataFrame({
        "transaction_date": ["2023-01-01"],
        "description": ["Test Transaction"],
        "amount": ["100.00"],
        "transaction_type": ["DEBIT"]
    })
    df.to_csv(csv_path, index=False)
    
    assert validator.validate(csv_path) is True

def test_validate_missing_columns(validator, tmp_path):
    csv_path = tmp_path / "missing_cols.csv"
    df = pd.DataFrame({
        "transaction_date": ["2023-01-01"],
        "amount": ["100.00"]
    })
    df.to_csv(csv_path, index=False)
    
    with pytest.raises(ValidationError, match="Missing required columns"):
        validator.validate(csv_path)

def test_validate_invalid_date(validator, tmp_path):
    csv_path = tmp_path / "invalid_date.csv"
    df = pd.DataFrame({
        "transaction_date": ["invalid-date"],
        "description": ["Test"],
        "amount": ["100.00"],
        "transaction_type": ["DEBIT"]
    })
    df.to_csv(csv_path, index=False)
    
    with pytest.raises(ValidationError, match="Invalid date format"):
        validator.validate(csv_path)

def test_validate_invalid_amount(validator, tmp_path):
    csv_path = tmp_path / "invalid_amount.csv"
    df = pd.DataFrame({
        "transaction_date": ["2023-01-01"],
        "description": ["Test"],
        "amount": ["100.005"], # Too many decimals
        "transaction_type": ["DEBIT"]
    })
    df.to_csv(csv_path, index=False)
    
    with pytest.raises(ValidationError, match="Amount has more than 2 decimal places"):
        validator.validate(csv_path)

def test_validate_invalid_transaction_type(validator, tmp_path):
    csv_path = tmp_path / "invalid_type.csv"
    df = pd.DataFrame({
        "transaction_date": ["2023-01-01"],
        "description": ["Test"],
        "amount": ["100.00"],
        "transaction_type": ["INVALID"]
    })
    df.to_csv(csv_path, index=False)
    
    with pytest.raises(ValidationError, match="Invalid transaction_type"):
        validator.validate(csv_path)
