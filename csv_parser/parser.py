import csv
from pathlib import Path
from typing import List, Generator
from decimal import Decimal
from datetime import datetime
from .models import TransactionRow

class CSVParser:
    def parse(self, csv_path: Path) -> List[TransactionRow]:
        rows: List[TransactionRow] = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Basic mapping - assuming standard columns for now, 
                # in a real app we'd have flexible mapping
                
                # Handle amount (remove $ and ,)
                amount_str = row.get("Amount", "0").replace("$", "").replace(",", "")
                amount = Decimal(amount_str)
                
                # Determine type
                t_type = "debit" if amount < 0 else "credit"
                
                # Parse date
                date_str = row.get("Date", "")
                try:
                    t_date = datetime.strptime(date_str, "%m/%d/%Y").date()
                except ValueError:
                    try:
                        t_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    except ValueError:
                        continue # Skip invalid dates

                rows.append(TransactionRow(
                    transaction_date=t_date,
                    description=row.get("Description", ""),
                    amount=amount,
                    transaction_type=t_type
                ))
        return rows
