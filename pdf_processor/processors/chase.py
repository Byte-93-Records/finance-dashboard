"""Chase processor using pdfplumber for PDF extraction."""

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


class ChaseProcessor(BaseProcessor):
    """
    Processor for Chase credit card statements.

    Chase statements have transactions in text format (not tables):
    MM/DD DESCRIPTION LOCATION AMOUNT
    Example: 12/08 LYFT *RIDE SUN 4AM HELP.LYFT.COM CA 105.94
    """

    FILENAME_PATTERNS = [
        r"chase",
        r"sapphire",
        r"freedom",
        r"slate",
        r"primevisa",
    ]

    # Pattern to match Chase transaction lines
    # Format: MM/DD DESCRIPTION AMOUNT (negative for credits)
    TRANSACTION_PATTERN = re.compile(
        r"^(\d{2}/\d{2})\s+(.+?)\s+(-?[\d,]+\.\d{2})$"
    )

    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds
        self._statement_year: Optional[int] = None

    @property
    def name(self) -> str:
        return "chase"

    def can_process(self, pdf_path: Path) -> bool:
        """Check if filename matches Chase patterns."""
        filename_lower = pdf_path.name.lower()
        return any(
            re.search(pattern, filename_lower) for pattern in self.FILENAME_PATTERNS
        )

    def extract(self, pdf_path: Path, output_dir: Path) -> Path:
        """Extract transactions from Chase PDF using text extraction."""
        try:
            logger.info(f"Processing Chase PDF: {pdf_path.name}")

            self._statement_year = self._extract_year_from_filename(pdf_path)

            transactions = []

            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    page_transactions = self._extract_transactions_from_text(text)
                    transactions.extend(page_transactions)

            if not transactions:
                raise ExtractionError("No transactions found in Chase PDF")

            df = pd.DataFrame(transactions)
            df = df[["transaction_date", "description", "amount", "transaction_type"]]

            output_path = output_dir / f"{pdf_path.stem}.csv"
            df.to_csv(output_path, index=False)

            logger.info(f"Extracted {len(df)} transactions to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Chase extraction failed: {e}")
            raise ExtractionError(f"Chase extraction failed: {e}")

    def _extract_year_from_filename(self, pdf_path: Path) -> int:
        """Extract year from filename."""
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

        Format: MM/DD DESCRIPTION AMOUNT
        Examples:
            12/08 LYFT *RIDE SUN 4AM HELP.LYFT.COM CA 105.94
            11/24 Payment Thank You-Mobile -4,000.00
        """
        # Must start with MM/DD pattern
        if not re.match(r"^\d{2}/\d{2}\s", line):
            return None

        # Try to extract date at start and amount at end
        match = self.TRANSACTION_PATTERN.match(line)
        if match:
            date_str, description, amount_str = match.groups()
            return self._create_transaction(date_str, description, amount_str)

        # Alternative: split and find amount at end
        parts = line.split()
        if len(parts) < 3:
            return None

        # First part should be date
        date_str = parts[0]
        if not re.match(r"^\d{2}/\d{2}$", date_str):
            return None

        # Last part should be amount
        amount_str = parts[-1]
        if not re.match(r"^-?[\d,]+\.\d{2}$", amount_str):
            return None

        # Everything in between is description
        description = " ".join(parts[1:-1])

        return self._create_transaction(date_str, description, amount_str)

    def _create_transaction(
        self, date_str: str, description: str, amount_str: str
    ) -> Dict:
        """Create a transaction dict from parsed values."""
        # Parse date (MM/DD -> YYYY-MM-DD)
        month, day = date_str.split("/")
        year = self._statement_year or datetime.now().year
        transaction_date = f"{year}-{int(month):02d}-{int(day):02d}"

        # Parse amount
        is_credit = amount_str.startswith("-")
        amount = Decimal(amount_str.replace(",", "").replace("-", ""))

        # For Chase: negative amounts are payments/credits, positive are charges
        transaction_type = "CREDIT" if is_credit else "DEBIT"

        return {
            "transaction_date": transaction_date,
            "description": description.strip(),
            "amount": str(amount),
            "transaction_type": transaction_type,
        }
