#!/usr/bin/env python3
"""
Extract key financial metrics from Amex CSV statement
"""
import csv
import json
from datetime import datetime
from collections import defaultdict
from decimal import Decimal

# Read the CSV file
csv_file = 'data/csv/amex_bluecash_all_2024.csv'

transactions = []
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            # Parse amount (negative = payment, positive = charge)
            amount = Decimal(row['Amount'])
            date_str = row['Date']
            date = datetime.strptime(date_str, '%m/%d/%Y')
            
            transactions.append({
                'date': date,
                'amount': amount,
                'description': row['Description'],
                'category': row['Category']
            })
        except (ValueError, KeyError) as e:
            print(f"Skipping row due to error: {e}")
            continue

# Sort by date
transactions.sort(key=lambda x: x['date'])

# Calculate metrics
total_charges = sum(t['amount'] for t in transactions if t['amount'] > 0)
total_payments = sum(abs(t['amount']) for t in transactions if t['amount'] < 0)
net_balance = total_charges - total_payments

# Group by month
monthly_data = defaultdict(lambda: {'charges': Decimal(0), 'payments': Decimal(0), 'transaction_count': 0})

for t in transactions:
    month_key = t['date'].strftime('%Y-%m')
    if t['amount'] > 0:
        monthly_data[month_key]['charges'] += t['amount']
    else:
        monthly_data[month_key]['payments'] += abs(t['amount'])
    monthly_data[month_key]['transaction_count'] += 1

# Calculate month-end balances (running total)
running_balance = Decimal(0)
monthly_balances = {}

for month in sorted(monthly_data.keys()):
    running_balance += monthly_data[month]['charges'] - monthly_data[month]['payments']
    monthly_balances[month] = float(running_balance)

# Prepare output
metrics = {
    "summary": {
        "year": 2024,
        "total_charges": float(total_charges),
        "total_payments": float(total_payments),
        "end_of_year_balance": float(net_balance),
        "transaction_count": len(transactions)
    },
    "monthly_balances": {
        month: {
            "end_of_month_balance": balance,
            "charges": float(monthly_data[month]['charges']),
            "payments": float(monthly_data[month]['payments']),
            "transaction_count": monthly_data[month]['transaction_count']
        }
        for month, balance in monthly_balances.items()
    }
}

# Save to JSON
output_file = 'data/json/amex_bluecash_2024_metrics.json'
with open(output_file, 'w') as f:
    json.dump(metrics, f, indent=2)

print(f"Metrics extracted and saved to {output_file}")
print(f"\nSummary:")
print(f"  Total Charges: ${total_charges:,.2f}")
print(f"  Total Payments: ${total_payments:,.2f}")
print(f"  End of Year Balance: ${net_balance:,.2f}")
print(f"\nMonthly end-of-month balances saved for {len(monthly_balances)} months")
