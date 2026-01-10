# Tasks: Bank-Specific PDF Processors

## 1. Create processor architecture
- [x] Create `processors/` directory with `base.py` abstract class
- [x] Implement `PDFRouter` in `router.py` with processor registry
- [x] Add pdfplumber to dependencies

## 2. Implement GenericProcessor (wrap existing Docling)
- [x] Create `processors/generic.py` that wraps existing `extractor.py`
- [x] Ensure no regression - all currently working PDFs still work

## 3. Implement AmexProcessor
- [x] Create `processors/amex.py` using pdfplumber text extraction
- [x] Handle Amex date format (MM/DD/YYYY) and amount parsing
- [x] Test with real Amex yearly statement (339 transactions extracted)

## 4. Implement ChaseProcessor
- [x] Create `processors/chase.py` using pdfplumber text extraction
- [x] Handle Chase text-based transaction format
- [x] Test with real Chase statements (72 transactions total)

## 5. Implement CitiProcessor
- [x] Create `processors/citi.py` (delegates to GenericProcessor/Docling)
- [ ] Verify existing Citi statements still process correctly

## 6. Update CLI to use router
- [x] Modify `cli.py` to use `PDFRouter` instead of `PDFExtractor` directly
- [x] Maintain same CLI interface (no breaking changes)
- [ ] Add `--processor` flag to force specific processor (optional)

## 7. Test with real PDFs
- [x] Test Amex yearly statements - 339 transactions
- [x] Test Chase statements - 48 + 24 = 72 transactions
- [ ] Test Citi statements (verify no regression)
- [x] Verify extracted CSVs match expected schema

## 8. Documentation
- [ ] Update `docs/` with supported banks and processor details
- [ ] Document how to add a new bank processor
