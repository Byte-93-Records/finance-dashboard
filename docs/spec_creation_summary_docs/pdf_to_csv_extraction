## ✅ OpenSpec Change Proposal Created Successfully!

I've created a comprehensive OpenSpec change proposal for the **Docling PDF to CSV extraction feature** at:

```
openspec/changes/add-pdf-to-csv-extraction/
```

### 📋 What Was Created:

1. **`proposal.md`** - High-level summary of why, what, and impact
   - Problem: Bank PDFs need structured extraction for ETL pipeline
   - Solution: Docling-based extraction with validation
   - Impact: New `pdf-extraction` capability, modified `etl-pipeline`

2. **`design.md`** - Detailed technical design document including:
   - Context & constraints (privacy-first, read-only PDFs)
   - Goals/Non-Goals (handles multiple banks, no OCR in v1)
   - Key decisions with rationale:
     - Why Docling over PyPDF2/pdfplumber
     - File system organization strategy
     - CSV schema standardization
     - Error handling approach
   - Architecture (module structure, processing flow)
   - Risks & mitigations (extraction accuracy, performance, schema evolution)
   - Migration plan & open questions

3. **`tasks.md`** - 63 implementation tasks organized in 10 phases:
   - Project setup (directories, dependencies, Docker)
   - Core module implementation (models, exceptions, handlers)
   - PDF extraction (Docling integration, timeouts)
   - CSV validation (schema checks, error handling)
   - Orchestration (CLI, logging, batch processing)
   - Testing (unit, integration, fixtures)
   - Configuration & documentation
   - Code quality (type hints, docstrings, linting)
   - Docker integration
   - Validation & deployment

4. **`specs/pdf-extraction/spec.md`** - New capability specification with 14 requirements:
   - Extract transactions from PDFs
   - CSV schema standardization
   - File system organization
   - Read-only processing
   - Batch processing support
   - Timeout handling
   - Error logging
   - Validation before ingestion
   - Multi-bank format support
   - Idempotent processing
   - Memory efficiency
   - CLI interface

5. **`specs/etl-pipeline/spec.md`** - Delta spec for existing capability:
   - **ADDED**: PDF extraction phase integration
   - **ADDED**: Extract phase configuration
   - **ADDED**: Extract phase monitoring
   - **MODIFIED**: ETL pipeline architecture (now 3-phase)
   - **MODIFIED**: Input data format (PDFs as primary)

### ✅ Validation Status:

```
✓ Change 'add-pdf-to-csv-extraction' is valid
✓ 0/63 tasks complete
✓ 2 capability specs defined (pdf-extraction, etl-pipeline)
```

### 🎯 Key Features:

- **Privacy-first**: All processing local, no external APIs
- **Read-only PDFs**: Originals never modified
- **ML-based extraction**: Docling handles varied bank formats
- **Robust validation**: CSV schema checks before database
- **Comprehensive error handling**: Failed PDFs isolated with logs
- **Testability**: 80% coverage target with fixture PDFs
- **Docker-native**: Full containerization with volume mounts

### 📝 Next Steps:

1. **Review the proposal** - Read through `proposal.md` and `design.md`
2. **Request approval** - Do not start implementation until proposal is approved
3. **Implement sequentially** - Follow tasks in `tasks.md` (63 tasks across 10 phases)
4. **Validate continuously** - Run `openspec validate add-pdf-to-csv-extraction --strict`
5. **Archive after deployment** - Move to `changes/archive/` when complete

The proposal is fully compliant with OpenSpec standards and aligns with your project's architecture patterns, tech stack, and conventions from project.md!

Made changes.