# Design: Bank-Specific PDF Processors

## Architecture

### Router Pattern

```
pdf_processor/
├── router.py                 # NEW: Routes PDFs to processors
├── processors/               # NEW: Bank-specific implementations
│   ├── __init__.py
│   ├── base.py              # Abstract base class
│   ├── amex.py              # Amex processor
│   ├── chase.py             # Chase processor
│   ├── citi.py              # Citi processor
│   └── generic.py           # Fallback (wraps existing Docling)
├── extractor.py             # EXISTING: Keep as-is, used by generic.py
├── cli.py                   # MODIFY: Use router instead of extractor directly
└── ...
```

### Processor Interface

```python
class BaseProcessor(ABC):
    @abstractmethod
    def can_process(self, pdf_path: Path) -> bool:
        """Return True if this processor can handle the PDF."""
        pass

    @abstractmethod
    def extract(self, pdf_path: Path, output_dir: Path) -> Path:
        """Extract transactions to CSV, return CSV path."""
        pass
```

### Router Logic

```python
class PDFRouter:
    def __init__(self):
        self.processors = [
            AmexProcessor(),
            ChaseProcessor(),
            CitiProcessor(),
            GenericProcessor(),  # Fallback, always last
        ]

    def route(self, pdf_path: Path) -> BaseProcessor:
        for processor in self.processors:
            if processor.can_process(pdf_path):
                return processor
        raise NoProcessorFoundError(pdf_path)
```

## Decisions

### 1. Filename-based routing (not PDF content)

**Decision**: Detect bank from filename pattern, not PDF content.

**Why**:
- Fast - no PDF parsing needed for routing
- Reliable - filenames follow known convention (`bank_card_month_year.pdf`)
- Simple - regex matching vs text extraction

**Trade-off**: Requires consistent filename convention. Acceptable for personal use.

### 2. pdfplumber over Docling for specific banks

**Decision**: Use pdfplumber for Amex/Chase, keep Docling as fallback.

**Why**:
- pdfplumber gives precise table coordinates
- Better handling of multi-line cells
- Faster for simple table extraction
- Docling's ML overhead not needed for structured statements

### 3. Processor priority order

**Decision**: Specific processors first, generic last.

```python
processors = [AmexProcessor, ChaseProcessor, CitiProcessor, GenericProcessor]
```

**Why**: Specific processors have stricter `can_process()` checks. Generic accepts anything.

### 4. Keep existing extractor.py

**Decision**: Don't modify `extractor.py`. Wrap it in `GenericProcessor`.

**Why**:
- No regression risk for working PDFs
- Clean separation - new code in new files
- Easy rollback if needed

## CSV Output Schema

All processors output the same schema (matches existing):

| Column | Type | Description |
|--------|------|-------------|
| transaction_date | YYYY-MM-DD | Transaction date |
| description | string | Merchant/payee |
| amount | decimal | Positive number, 2 decimals |
| transaction_type | DEBIT/CREDIT | Expense or income |

## Error Handling

- Processor failure → log error, move PDF to `failed/`, continue batch
- No processor found → use GenericProcessor (never fails to attempt)
- Partial extraction → save what was extracted, log warning
