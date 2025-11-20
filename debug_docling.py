from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.document_converter import DocumentConverter, InputFormat

try:
    print("Initializing PdfPipelineOptions...")
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
    print("PdfPipelineOptions initialized successfully.")
    
    print("Initializing DocumentConverter...")
    converter = DocumentConverter(
        allowed_formats=[InputFormat.PDF],
        format_options={
            InputFormat.PDF: pipeline_options
        }
    )
    print("DocumentConverter initialized successfully.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
