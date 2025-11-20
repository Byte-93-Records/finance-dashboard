# CSV Schema Documentation

The PDF processor extracts financial transactions into a standardized CSV format. This document describes the schema of the output CSV files.

## File Naming Convention
Output files are named using the original PDF filename with a `.csv` extension:
`[original_filename].csv`

## Columns

| Column Name | Data Type | Required | Description | Example |
|-------------|-----------|----------|-------------|---------|
| `transaction_date` | Date (ISO 8601) | Yes | Date of the transaction in YYYY-MM-DD format. | `2023-10-25` |
| `description` | String | Yes | Description or payee of the transaction. | `STARBUCKS STORE 12345` |
| `amount` | Decimal | Yes | Transaction amount. Positive for both debits and credits (see `transaction_type`). Max 2 decimal places. | `5.45` |
| `transaction_type` | String | Yes | Type of transaction: `DEBIT` or `CREDIT`. | `DEBIT` |
| `category` | String | No | Optional category if available in source. | `Dining` |

## Data Validation Rules

1.  **Date Format**: Must be a valid date in `YYYY-MM-DD` format.
2.  **Amount Precision**: Must be a decimal number with at most 2 decimal places.
3.  **Transaction Type**: Must be exactly `DEBIT` or `CREDIT`.
