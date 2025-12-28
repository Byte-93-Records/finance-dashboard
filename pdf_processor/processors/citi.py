"""Citi processor - currently uses generic Docling as Citi PDFs work well with it."""

import re
import logging
from pathlib import Path

from .base import BaseProcessor
from .generic import GenericProcessor

logger = logging.getLogger(__name__)


class CitiProcessor(BaseProcessor):
    """
    Processor for Citi credit card statements.

    Currently delegates to GenericProcessor since Citi PDFs
    work well with Docling extraction. This class exists to:
    1. Explicitly route Citi PDFs
    2. Allow future Citi-specific optimizations
    """

    FILENAME_PATTERNS = [
        r"citi",
        r"thankyou",
        r"costco.?visa",
        r"double.?cash",
    ]

    def __init__(self, timeout_seconds: int = 30):
        self._generic = GenericProcessor(timeout_seconds=timeout_seconds)

    @property
    def name(self) -> str:
        return "citi"

    def can_process(self, pdf_path: Path) -> bool:
        """Check if filename matches Citi patterns."""
        filename_lower = pdf_path.name.lower()
        return any(
            re.search(pattern, filename_lower) for pattern in self.FILENAME_PATTERNS
        )

    def extract(self, pdf_path: Path, output_dir: Path) -> Path:
        """Extract using generic Docling processor (works well for Citi)."""
        logger.info(f"Processing Citi PDF: {pdf_path.name} (using Docling)")
        return self._generic.extract(pdf_path, output_dir)
