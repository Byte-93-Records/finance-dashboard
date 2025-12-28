"""Generic processor using Docling for PDF extraction."""

from pathlib import Path

from .base import BaseProcessor
from ..extractor import PDFExtractor


class GenericProcessor(BaseProcessor):
    """
    Fallback processor using Docling.

    Wraps the existing PDFExtractor for backward compatibility.
    Used when no bank-specific processor matches.
    """

    def __init__(self, timeout_seconds: int = 30):
        self._extractor = PDFExtractor(timeout_seconds=timeout_seconds)

    @property
    def name(self) -> str:
        return "generic"

    def can_process(self, pdf_path: Path) -> bool:
        """Generic processor accepts any PDF as fallback."""
        return True

    def extract(self, pdf_path: Path, output_dir: Path) -> Path:
        """Extract using Docling (existing implementation)."""
        return self._extractor.extract(pdf_path, output_dir)
