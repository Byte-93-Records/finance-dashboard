import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from pathlib import Path
from pdf_processor.cli import cli, process
from pdf_processor.exceptions import ExtractionError

@pytest.fixture
def runner():
    return CliRunner()

@patch("pdf_processor.cli.FileHandler")
@patch("pdf_processor.cli.PDFExtractor")
@patch("pdf_processor.cli.CSVValidator")
def test_process_flow_success(mock_validator_cls, mock_extractor_cls, mock_handler_cls, runner, tmp_path):
    # Setup mocks
    mock_handler = mock_handler_cls.return_value
    mock_extractor = mock_extractor_cls.return_value
    mock_validator = mock_validator_cls.return_value
    
    # Mock file list
    pdf_path = Path("data/pdfs/test.pdf")
    mock_handler.list_pending_pdfs.return_value = [pdf_path]
    
    # Mock extraction
    csv_path = Path("data/csv/test.csv")
    mock_extractor.extract.return_value = csv_path
    
    # Mock validation
    mock_validator.validate.return_value = True
    
    # Run CLI
    result = runner.invoke(process)
    
    assert result.exit_code == 0
    assert "Processing complete" in result.output
    
    # Verify calls
    mock_extractor.extract.assert_called_once()
    mock_validator.validate.assert_called_once_with(csv_path)
    mock_handler.move_to_processed.assert_called_once_with(pdf_path)

@patch("pdf_processor.cli.FileHandler")
@patch("pdf_processor.cli.PDFExtractor")
def test_process_flow_extraction_fail(mock_extractor_cls, mock_handler_cls, runner):
    mock_handler = mock_handler_cls.return_value
    mock_extractor = mock_extractor_cls.return_value
    
    pdf_path = Path("data/pdfs/test.pdf")
    mock_handler.list_pending_pdfs.return_value = [pdf_path]
    
    mock_extractor.extract.side_effect = ExtractionError("Extraction failed")
    
    result = runner.invoke(process)
    
    assert result.exit_code == 0 # Should not crash
    
    mock_handler.move_to_failed.assert_called_once()
    args = mock_handler.move_to_failed.call_args
    assert args[0][0] == pdf_path
    assert "Extraction failed" in args[0][1]

@patch("pdf_processor.cli.FileHandler")
def test_process_dry_run(mock_handler_cls, runner):
    mock_handler = mock_handler_cls.return_value
    pdf_path = Path("data/pdfs/test.pdf")
    mock_handler.list_pending_pdfs.return_value = [pdf_path]
    
    result = runner.invoke(process, ["--dry-run"])
    
    assert result.exit_code == 0
    assert "Dry run" in result.output
    
    # Should not call move methods
    mock_handler.move_to_processed.assert_not_called()
    mock_handler.move_to_failed.assert_not_called()
