from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
import logging

logging.basicConfig(level=logging.INFO)

try:
    print("Initializing PdfPipelineOptions...")
    pipeline_options = PdfPipelineOptions()
    print("PdfPipelineOptions initialized.")
    print(f"Attributes: {dir(pipeline_options)}")
    
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
    
    print("Initializing DocumentConverter...")
    converter = DocumentConverter(
        allowed_formats=[InputFormat.PDF],
        format_options={
            InputFormat.PDF: pipeline_options
        }
    )
    print("DocumentConverter initialized.")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
