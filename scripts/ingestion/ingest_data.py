#!/usr/bin/env python3
"""Simple CSV ingestion script for finance dashboard"""
import csv
import hashlib
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import os
import sys

# Add parent directory to path
sys.path.insert(0, '/app')

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from database.models import Base, Account, Transaction

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://finance:finance@postgres:5432/finance_db")

def parse_amount(amount_str):
    """Parse amount string to Decimal"""
    if not amount_str:
        return None
    # Remove $, commas, +, and whitespace
    cleaned = amount_str.replace('$', '').replace(',', '').replace('+', '').strip()
    if not cleaned or cleaned == '-' or not cleaned.replace('.', '').replace('-', '').isdigit():
        return None
    try:
        return Decimal(cleaned)
    except:
        return None

def hash_transaction(account_id, date, amount, description):
    """Generate unique hash for transaction"""
    norm_desc = " ".join(description.lower().split())
    raw = f"{account_id}|{date}|{amount}|{norm_desc}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def ingest_csv(csv_path: str, account_id: int):
    """Ingest CSV file into database"""
    from csv_parser.filename_parser import parse_filename
    
    # Parse filename for bank and card info
    file_info = parse_filename(csv_path)
    
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Get or create account
        account = session.get(Account, account_id)
        if not account:
            account_name = f"{file_info['bank_name']} {file_info['card_name']}" if file_info['bank_name'] else "Test Account"
            
            account = Account(
                id=account_id,
                name=account_name,
                account_type="credit_card",
                institution=file_info['bank_name'],
                bank_name=file_info['bank_name'],
                card_name=file_info['card_name']
            )
            session.add(account)
            session.commit()
            print(f"Created account: {account.name} (Bank: {account.bank_name}, Card: {account.card_name})")
        
        transactions = []
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 3:
                    continue
                    
                # Skip header rows and summary rows
                if row[0] in ['Previous balance', 'Payments', 'Credits', 'Purchases', 
                              'Cash advances', 'Fees', 'Interest', 'New balance',
                              'Credit Limit', '0']:
                    continue
                
                # Heuristic parsing: find date, description, and amount columns
                date_str = None
                description = ""
                amount_str = None
                
                # 1. Find date (MM/DD format)
                date_idx = -1
                for i, col in enumerate(row):
                    if col and '/' in col and len(col) <= 10:
                        # Simple check for date-like string
                        try:
                            parts = col.split('/')
                            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                                date_str = col
                                date_idx = i
                                break
                        except:
                            pass
                
                if not date_str:
                    continue
                    
                # 2. Find amount (starts with $ or -$)
                amount_idx = -1
                for i, col in enumerate(row):
                    if i == date_idx: continue
                    if col and ('$' in col or (col.replace('.','').replace('-','').isdigit() and '.' in col)):
                        # Check if it looks like a valid amount
                        if parse_amount(col) is not None:
                            amount_str = col
                            amount_idx = i
                            break
                
                if not amount_str:
                    continue
                    
                # 3. Find description (longest string that isn't date or amount)
                desc_candidates = []
                for i, col in enumerate(row):
                    if i == date_idx or i == amount_idx: continue
                    if col and len(col) > 3:
                        desc_candidates.append(col)
                
                if desc_candidates:
                    # Pick the longest one as description
                    description = max(desc_candidates, key=len)
                else:
                    description = "Unknown Transaction"

                # Parse date
                try:
                    # Handle MM/DD or MM/DD/YY
                    parts = date_str.split('/')
                    if len(parts) == 2:
                        t_date = datetime.strptime(date_str, "%m/%d").replace(year=2025).date()
                    elif len(parts) == 3:
                        fmt = "%m/%d/%y" if len(parts[2]) == 2 else "%m/%d/%Y"
                        t_date = datetime.strptime(date_str, fmt).date()
                    else:
                        continue
                except:
                    continue
                
                # Parse amount
                amount = parse_amount(amount_str)
                if amount is None:
                    continue
                
                # Determine type
                t_type = "debit" if amount < 0 else "credit"
                
                # Generate hash
                t_hash = hash_transaction(account_id, t_date, abs(amount), description)
                
                # Check if exists
                existing = session.query(Transaction).filter_by(transaction_hash=t_hash).first()
                if existing:
                    continue
                
                # Create transaction
                transaction = Transaction(
                    account_id=account_id,
                    transaction_date=t_date,
                    description=description,
                    amount=amount,
                    transaction_type=t_type,  
                    transaction_hash=t_hash
                )
                transactions.append(transaction)
        
        # Bulk insert
        if transactions:
            session.add_all(transactions)
            session.commit()
            print(f"✓ Imported {len(transactions)} transactions")
        else:
            print("No new transactions to import")

if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "/data/csv/April 03_20251120_090048_20251120_090337.csv"
    account_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    print(f"Ingesting {csv_file} into account {account_id}...")
    ingest_csv(csv_file, account_id)
    print("Done!")
