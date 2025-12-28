# Tasks: Bank-Specific PDF Processors

## 1. Create processor architecture
- [ ] Create `processors/` directory with `base.py` abstract class
- [ ] Implement `PDFRouter` in `router.py` with processor registry
- [ ] Add pdfplumber to dependencies

## 2. Implement GenericProcessor (wrap existing Docling)
- [ ] Create `processors/generic.py` that wraps existing `extractor.py`
- [ ] Ensure no regression - all currently working PDFs still work

## 3. Implement AmexProcessor
- [ ] Create `processors/amex.py` using pdfplumber
- [ ] Handle Amex multi-line descriptions (join wrapped text)
- [ ] Handle Amex date format and amount parsing
- [ ] Test with real Amex yearly statement

## 4. Implement ChaseProcessor
- [ ] Create `processors/chase.py` using pdfplumber
- [ ] Handle Chase table structure
- [ ] Test with real Chase statement

## 5. Implement CitiProcessor
- [ ] Create `processors/citi.py` (may just use generic if working)
- [ ] Verify existing Citi statements still process correctly

## 6. Update CLI to use router
- [ ] Modify `cli.py` to use `PDFRouter` instead of `PDFExtractor` directly
- [ ] Maintain same CLI interface (no breaking changes)
- [ ] Add `--processor` flag to force specific processor (optional)

## 7. Test with real PDFs
- [ ] Test Amex yearly statements (currently failing)
- [ ] Test Chase statements (currently failing)
- [ ] Test Citi statements (verify no regression)
- [ ] Verify extracted CSVs match expected transaction counts

## 8. Documentation
- [ ] Update `docs/` with supported banks and processor details
- [ ] Document how to add a new bank processor
