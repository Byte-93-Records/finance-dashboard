"""Abstract base class for PDF processors."""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseProcessor(ABC):
    """Abstract base class for bank-specific PDF processors."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable processor name."""
        pass

    @abstractmethod
    def can_process(self, pdf_path: Path) -> bool:
        """
        Check if this processor can handle the given PDF.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            True if this processor should handle the PDF.
        """
        pass

    @abstractmethod
    def extract(self, pdf_path: Path, output_dir: Path) -> Path:
        """
        Extract transactions from PDF and save as CSV.

        Args:
            pdf_path: Path to the PDF file.
            output_dir: Directory to save the CSV file.

        Returns:
            Path to the generated CSV file.

        Raises:
            ExtractionError: If extraction fails.
        """
        pass
