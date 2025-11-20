import pytest
from pathlib import Path
from pdf_processor.file_handler import FileHandler

@pytest.fixture
def file_handler(tmp_path):
    input_dir = tmp_path / "pdfs"
    processed_dir = tmp_path / "processed"
    failed_dir = tmp_path / "failed"
    return FileHandler(input_dir, processed_dir, failed_dir)

def test_list_pending_pdfs(file_handler):
    # Create dummy PDFs
    (file_handler.input_dir / "test1.pdf").touch()
    (file_handler.input_dir / "test2.pdf").touch()
    (file_handler.input_dir / "not_pdf.txt").touch()
    
    pdfs = file_handler.list_pending_pdfs()
    assert len(pdfs) == 2
    assert any(p.name == "test1.pdf" for p in pdfs)
    assert any(p.name == "test2.pdf" for p in pdfs)

def test_move_to_processed(file_handler):
    pdf_path = file_handler.input_dir / "test.pdf"
    pdf_path.touch()
    
    new_path = file_handler.move_to_processed(pdf_path)
    
    assert not pdf_path.exists()
    assert new_path.exists()
    assert new_path.parent == file_handler.processed_dir
    assert "test" in new_path.name

def test_move_to_failed(file_handler):
    pdf_path = file_handler.input_dir / "test.pdf"
    pdf_path.touch()
    
    new_path = file_handler.move_to_failed(pdf_path, "Error message")
    
    assert not pdf_path.exists()
    assert new_path.exists()
    assert new_path.parent == file_handler.failed_dir
    
    # Check log file
    log_path = new_path.with_suffix(".error.log")
    assert log_path.exists()
    assert "Error message" in log_path.read_text()
