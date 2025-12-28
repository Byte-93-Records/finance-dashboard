"""Discover processor using pdfplumber for PDF extraction."""

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


class DiscoverProcessor(BaseProcessor):
    """
    Processor for Discover credit card statements.

    Discover statements have transactions in text format:
    MM/DD/YY MM/DD/YY DESCRIPTION $ AMOUNT Category
    Example: 12/02/25 12/02/25 KATE SPADE 33224 SANTA CLARA CA $ 195.78 Merchandise
    """

    FILENAME_PATTERNS = [
        r"discover",
        r"discover.?it",
    ]

    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds

    @property
    def name(self) -> str:
        return "discover"

    def can_process(self, pdf_path: Path) -> bool:
        """Check if filename matches Discover patterns."""
        filename_lower = pdf_path.name.lower()
        return any(
            re.search(pattern, filename_lower) for pattern in self.FILENAME_PATTERNS
        )

    def extract(self, pdf_path: Path, output_dir: Path) -> Path:
        """Extract transactions from Discover PDF using text extraction."""
        try:
            logger.info(f"Processing Discover PDF: {pdf_path.name}")

            # Try to get year from filename
            self._statement_year = self._extract_year_from_filename(pdf_path)

            transactions = []

            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    page_transactions = self._extract_transactions_from_text(text)
                    transactions.extend(page_transactions)

            if not transactions:
                raise ExtractionError("No transactions found in Discover PDF")

            df = pd.DataFrame(transactions)
            df = df[["transaction_date", "description", "amount", "transaction_type"]]

            output_path = output_dir / f"{pdf_path.stem}.csv"
            df.to_csv(output_path, index=False)

            logger.info(f"Extracted {len(df)} transactions to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Discover extraction failed: {e}")
            raise ExtractionError(f"Discover extraction failed: {e}")

    def _extract_year_from_filename(self, pdf_path: Path) -> int:
        """Extract year from filename."""
        # Check for 4-digit year
        match = re.search(r"20\d{2}", pdf_path.name)
        if match:
            return int(match.group())
        return datetime.now().year

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

        Discover format: MM/DD/YY MM/DD/YY DESCRIPTION $ AMOUNT Category
        Examples:
            12/02/25 12/02/25 KATE SPADE 33224 SANTA CLARA CA $ 195.78 Merchandise
            11/29/25 11/29/25 INTERNET PAYMENT - THANK YOU $ -80.00 Payments and Credits
        """
        # Must start with MM/DD/YY pattern (transaction date + posting date)
        if not re.match(r"^\d{2}/\d{2}/\d{2}\s+\d{2}/\d{2}/\d{2}\s", line):
            return None

        # Extract the two dates at the start
        date_match = re.match(r"^(\d{2}/\d{2}/\d{2})\s+(\d{2}/\d{2}/\d{2})\s+(.+)$", line)
        if not date_match:
            return None

        trans_date_str = date_match.group(1)
        # post_date_str = date_match.group(2)  # We use transaction date
        rest = date_match.group(3)

        # Find amount pattern: $ followed by optional negative, digits, decimal
        # Amount is before the category (last word(s))
        amount_match = re.search(r"\$\s*(-?[\d,]+\.\d{2})\s+\w+", rest)
        if not amount_match:
            # Try without category at end
            amount_match = re.search(r"\$\s*(-?[\d,]+\.\d{2})\s*$", rest)

        if not amount_match:
            return None

        amount_str = amount_match.group(1)

        # Description is everything before the $ amount
        description = rest[:amount_match.start()].strip()

        if not description:
            return None

        return self._create_transaction(trans_date_str, description, amount_str)

    def _create_transaction(
        self, date_str: str, description: str, amount_str: str
    ) -> Dict:
        """Create a transaction dict from parsed values."""
        # Parse date (MM/DD/YY -> YYYY-MM-DD)
        month, day, year = date_str.split("/")
        year_full = 2000 + int(year) if int(year) < 100 else int(year)
        transaction_date = f"{year_full}-{int(month):02d}-{int(day):02d}"

        # Parse amount
        is_credit = amount_str.startswith("-")
        amount = Decimal(amount_str.replace(",", "").replace("-", ""))

        # For Discover: negative amounts are payments/credits, positive are charges
        transaction_type = "CREDIT" if is_credit else "DEBIT"

        return {
            "transaction_date": transaction_date,
            "description": description.strip(),
            "amount": str(amount),
            "transaction_type": transaction_type,
        }
