import logging
import signal
import pandas as pd
from pathlib import Path
from typing import Optional, List
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode

from .exceptions import ExtractionError

logger = logging.getLogger(__name__)

class PDFExtractor:
    """Extracts tables from PDF files using Docling."""
    
    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds
        self._converter = self._configure_converter()
        
    def _configure_converter(self) -> DocumentConverter:
        """Configure Docling converter for financial statements."""
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False  # Assume text-based PDFs for speed
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
        
        return DocumentConverter(
            allowed_formats=[InputFormat.PDF],
            format_options={
                InputFormat.PDF: pipeline_options
            }
        )

    def _timeout_handler(self, signum, frame):
        raise TimeoutError("PDF processing timed out")

    def extract(self, pdf_path: Path, output_dir: Path) -> Path:
        """
        Extract tables from a PDF and save as CSV.
        
        Args:
            pdf_path: Path to the PDF file.
            output_dir: Directory to save the CSV file.
            
        Returns:
            Path to the generated CSV file.
        """
        try:
            # Set timeout
            signal.signal(signal.SIGALRM, self._timeout_handler)
            signal.alarm(self.timeout_seconds)
            
            logger.info(f"Starting extraction for {pdf_path.name}")
            
            # Convert
            result = self._converter.convert(pdf_path)
            
            # Extract tables
            # We assume the financial statement has one main table or we concatenate them
            # For simplicity, let's take all tables found and concatenate them, 
            # or just take the largest one?
            # Financial statements often have multiple pages with tables.
            # We should probably concatenate all tables that look like transaction lists.
            
            tables = []
            for table in result.document.tables:
                # Convert to pandas DataFrame
                df = table.export_to_dataframe()
                if not df.empty:
                    tables.append(df)
            
            if not tables:
                raise ExtractionError("No tables found in PDF")
            
            # Concatenate all tables
            # This is a naive approach, might need refinement for specific bank formats
            # but good for a start.
            combined_df = pd.concat(tables, ignore_index=True)
            
            # Save to CSV
            output_path = output_dir / f"{pdf_path.stem}.csv"
            combined_df.to_csv(output_path, index=False)
            
            logger.info(f"Extracted {len(combined_df)} rows to {output_path}")
            return output_path
            
        except TimeoutError:
            raise ExtractionError(f"Processing timed out after {self.timeout_seconds}s")
        except Exception as e:
            raise ExtractionError(f"Extraction failed: {e}")
        finally:
            signal.alarm(0)  # Disable alarm
