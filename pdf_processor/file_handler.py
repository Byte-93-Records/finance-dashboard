import shutil
import logging
from pathlib import Path
from typing import List
from datetime import datetime
from .exceptions import FileHandlerError

logger = logging.getLogger(__name__)

class FileHandler:
    """Handles file operations for the PDF processor."""
    
    def __init__(self, input_dir: Path, processed_dir: Path, failed_dir: Path):
        self.input_dir = input_dir
        self.processed_dir = processed_dir
        self.failed_dir = failed_dir
        
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure all directories exist."""
        try:
            self.input_dir.mkdir(parents=True, exist_ok=True)
            self.processed_dir.mkdir(parents=True, exist_ok=True)
            self.failed_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise FileHandlerError(f"Failed to create directories: {e}")

    def list_pending_pdfs(self) -> List[Path]:
        """List all PDF files in the input directory."""
        try:
            return list(self.input_dir.glob("*.pdf"))
        except OSError as e:
            raise FileHandlerError(f"Failed to list PDFs: {e}")

    def move_to_processed(self, pdf_path: Path) -> Path:
        """Move a PDF file to the processed directory."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_path = self.processed_dir / f"{pdf_path.stem}_{timestamp}{pdf_path.suffix}"
            shutil.move(str(pdf_path), str(dest_path))
            logger.info(f"Moved {pdf_path.name} to {dest_path}")
            return dest_path
        except OSError as e:
            raise FileHandlerError(f"Failed to move file to processed: {e}")

    def move_to_failed(self, pdf_path: Path, error_msg: str) -> Path:
        """Move a PDF file to the failed directory and write an error log."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_path = self.failed_dir / f"{pdf_path.stem}_{timestamp}{pdf_path.suffix}"
            shutil.move(str(pdf_path), str(dest_path))
            
            # Write error log
            log_path = dest_path.with_suffix(".error.log")
            with open(log_path, "w") as f:
                f.write(f"Error processing {pdf_path.name}:\n{error_msg}\n")
                
            logger.error(f"Moved {pdf_path.name} to {dest_path} due to error")
            return dest_path
        except OSError as e:
            raise FileHandlerError(f"Failed to move file to failed: {e}")
