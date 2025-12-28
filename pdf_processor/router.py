"""PDF Router - routes PDFs to appropriate bank-specific processors."""

import logging
from pathlib import Path
from typing import List, Optional

from .processors.base import BaseProcessor
from .processors.generic import GenericProcessor
from .processors.amex import AmexProcessor
from .processors.chase import ChaseProcessor
from .processors.citi import CitiProcessor
from .processors.discover import DiscoverProcessor
from .exceptions import ExtractionError

logger = logging.getLogger(__name__)


class PDFRouter:
    """
    Routes PDF files to bank-specific processors based on filename.

    Processors are checked in order. First matching processor handles the PDF.
    GenericProcessor is always last as fallback.
    """

    def __init__(self, timeout_seconds: int = 30):
        """
        Initialize router with available processors.

        Args:
            timeout_seconds: Timeout for extraction operations.
        """
        self.timeout_seconds = timeout_seconds
        self._processors: List[BaseProcessor] = self._build_processor_list()

    def _build_processor_list(self) -> List[BaseProcessor]:
        """
        Build ordered list of processors.

        Bank-specific processors first, generic fallback last.
        """
        processors = [
            AmexProcessor(self.timeout_seconds),
            ChaseProcessor(self.timeout_seconds),
            CitiProcessor(self.timeout_seconds),
            DiscoverProcessor(self.timeout_seconds),
            GenericProcessor(self.timeout_seconds),  # Fallback, always last
        ]

        return processors

    def get_processor(self, pdf_path: Path) -> BaseProcessor:
        """
        Find the appropriate processor for a PDF.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            The processor that should handle this PDF.
        """
        for processor in self._processors:
            if processor.can_process(pdf_path):
                logger.info(f"Selected {processor.name} processor for {pdf_path.name}")
                return processor

        # Should never reach here since GenericProcessor accepts all
        raise ExtractionError(f"No processor found for {pdf_path.name}")

    def extract(self, pdf_path: Path, output_dir: Path) -> Path:
        """
        Extract transactions from PDF using appropriate processor.

        Args:
            pdf_path: Path to the PDF file.
            output_dir: Directory to save the CSV file.

        Returns:
            Path to the generated CSV file.
        """
        processor = self.get_processor(pdf_path)
        return processor.extract(pdf_path, output_dir)

    @property
    def processors(self) -> List[BaseProcessor]:
        """List of available processors."""
        return self._processors
