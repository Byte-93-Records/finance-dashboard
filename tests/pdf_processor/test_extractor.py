import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import pandas as pd
from pdf_processor.extractor import PDFExtractor, ExtractionError

@pytest.fixture
def mock_converter_cls():
    with patch("pdf_processor.extractor.DocumentConverter") as mock:
        yield mock

def test_extract_success(mock_converter_cls, tmp_path):
    # Mock converter instance
    mock_converter = mock_converter_cls.return_value
    
    # Mock conversion result
    mock_result = MagicMock()
    mock_table = MagicMock()
    
    # Create a dummy dataframe
    df = pd.DataFrame({"col1": ["val1"], "col2": ["val2"]})
    mock_table.export_to_dataframe.return_value = df
    
    mock_result.document.tables = [mock_table]
    mock_converter.convert.return_value = mock_result
    
    # Initialize extractor (will use mocked DocumentConverter)
    extractor = PDFExtractor()
    
    # Setup paths
    pdf_path = tmp_path / "test.pdf"
    pdf_path.touch()
    output_dir = tmp_path / "csv"
    output_dir.mkdir()
    
    # Run extraction
    csv_path = extractor.extract(pdf_path, output_dir)
    
    # Verify
    assert csv_path.exists()
    assert csv_path.parent == output_dir
    assert csv_path.name == "test.csv"
    
    # Verify content
    saved_df = pd.read_csv(csv_path)
    assert len(saved_df) == 1
    assert saved_df.iloc[0]["col1"] == "val1"

def test_extract_no_tables(mock_converter_cls, tmp_path):
    mock_converter = mock_converter_cls.return_value
    mock_result = MagicMock()
    mock_result.document.tables = []
    mock_converter.convert.return_value = mock_result
    
    extractor = PDFExtractor()
    
    pdf_path = tmp_path / "test.pdf"
    pdf_path.touch()
    output_dir = tmp_path
    
    with pytest.raises(ExtractionError, match="No tables found"):
        extractor.extract(pdf_path, output_dir)

def test_extract_timeout(mock_converter_cls, tmp_path):
    # We can't easily test signal.alarm with mock, but we can test the handler
    extractor = PDFExtractor(timeout_seconds=1)
    
    with pytest.raises(TimeoutError):
        extractor._timeout_handler(None, None)
