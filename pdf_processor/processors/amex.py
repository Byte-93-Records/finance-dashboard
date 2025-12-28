"""Amex processor using pdfplumber for PDF extraction."""

import re
import logging
from decimal import Decimal
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

import pandas as pd
import pdfplumber

from .base import BaseProcessor
from ..exceptions import ExtractionError

logger = logging.getLogger(__name__)


class AmexProcessor(BaseProcessor):
    """
    Processor for American Express credit card statements.

    Amex statements have transactions in text format:
    MM/DD/YYYY Month Description Amount B/P
    Example: 03/18/2024 April AplPay THE UPS STORETEMPE AZ 21.62 B/P
    """

    FILENAME_PATTERNS = [
        r"amex",
        r"american.?express",
        r"bluecash",
        r"platinum",
        r"gold.?card",
    ]

    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds

    @property
    def name(self) -> str:
        return "amex"

    def can_process(self, pdf_path: Path) -> bool:
        """Check if filename matches Amex patterns."""
        filename_lower = pdf_path.name.lower()
        return any(
            re.search(pattern, filename_lower) for pattern in self.FILENAME_PATTERNS
        )

    def extract(self, pdf_path: Path, output_dir: Path) -> Path:
        """Extract transactions from Amex PDF using text extraction."""
        try:
            logger.info(f"Processing Amex PDF: {pdf_path.name}")

            transactions = []

            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    page_transactions = self._extract_transactions_from_text(text)
                    transactions.extend(page_transactions)

            if not transactions:
                raise ExtractionError("No transactions found in Amex PDF")

            # Remove duplicates (same date, description, amount)
            seen = set()
            unique_transactions = []
            for t in transactions:
                key = (t["transaction_date"], t["description"], t["amount"])
                if key not in seen:
                    seen.add(key)
                    unique_transactions.append(t)

            df = pd.DataFrame(unique_transactions)
            df = df[["transaction_date", "description", "amount", "transaction_type"]]

            output_path = output_dir / f"{pdf_path.stem}.csv"
            df.to_csv(output_path, index=False)

            logger.info(f"Extracted {len(df)} transactions to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Amex extraction failed: {e}")
            raise ExtractionError(f"Amex extraction failed: {e}")

    def _extract_transactions_from_text(self, text: str) -> List[Dict]:
        """Extract transactions from page text."""
        transactions = []

        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue

            transaction = self._parse_transaction_line(line)
            if transaction:
                transactions.append(transaction)

        return transactions

    def _parse_transaction_line(self, line: str) -> Optional[Dict]:
        """
        Parse a line that looks like a transaction.

        Amex format: MM/DD/YYYY Month Description Amount [B/P]
        Examples:
            03/18/2024 April AplPay THE UPS STORETEMPE AZ 21.62 B/P
            01/30/2024 February AplPay OM BEAUTY SALMilpitas CA 11.50 B/P
            12/15/2024 PAYMENT RECEIVED - THANK YOU -500.00
        """
        # Must start with MM/DD/YYYY pattern
        if not re.match(r"^\d{2}/\d{2}/\d{4}\s", line):
            return None

        # Extract date
        date_match = re.match(r"^(\d{2}/\d{2}/\d{4})", line)
        if not date_match:
            return None

        date_str = date_match.group(1)
        rest = line[len(date_str):].strip()

        # Look for amount at end (before optional B/P suffix)
        # Amount pattern: optional negative, digits with optional commas, decimal, 2 digits
        amount_pattern = r"(-?[\d,]+\.\d{2})(?:\s*B/P)?$"
        amount_match = re.search(amount_pattern, rest)

        if not amount_match:
            return None

        amount_str = amount_match.group(1)
        description = rest[:amount_match.start()].strip()

        # Remove month name from start of description if present
        month_pattern = r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s+"
        description = re.sub(month_pattern, "", description, flags=re.IGNORECASE)

        if not description:
            return None

        return self._create_transaction(date_str, description, amount_str)

    def _create_transaction(
        self, date_str: str, description: str, amount_str: str
    ) -> Dict:
        """Create a transaction dict from parsed values."""
        # Parse date (MM/DD/YYYY -> YYYY-MM-DD)
        month, day, year = date_str.split("/")
        transaction_date = f"{year}-{int(month):02d}-{int(day):02d}"

        # Parse amount
        is_credit = amount_str.startswith("-")
        amount = Decimal(amount_str.replace(",", "").replace("-", ""))

        # For Amex: negative amounts are payments/credits, positive are charges
        transaction_type = "CREDIT" if is_credit else "DEBIT"

        return {
            "transaction_date": transaction_date,
            "description": self._clean_description(description),
            "amount": str(amount),
            "transaction_type": transaction_type,
        }

    def _clean_description(self, description: str) -> str:
        """Clean up description text."""
        # Remove extra whitespace
        description = " ".join(description.split())
        return description.strip()
