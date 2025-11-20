class PDFProcessorError(Exception):
    """Base exception for all PDF processor errors."""
    pass

class ExtractionError(PDFProcessorError):
    """Raised when PDF extraction fails."""
    pass

class ValidationError(PDFProcessorError):
    """Raised when data validation fails."""
    pass

class FileHandlerError(PDFProcessorError):
    """Raised when file operations fail."""
    pass
