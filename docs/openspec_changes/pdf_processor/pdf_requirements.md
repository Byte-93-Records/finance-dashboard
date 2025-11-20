# PDF Requirements

To ensure successful extraction of financial data, input PDF files must meet the following requirements.

## Supported Formats

The system is optimized for standard US financial statements from:
*   **Banks**: Chase, Bank of America, Wells Fargo, Citi, Capital One
*   **Credit Cards**: Amex, Visa, Mastercard, Discover
*   **Brokerages**: Fidelity, Schwab, TD Ameritrade, E*TRADE

## Technical Requirements

1.  **Text-Based**: PDFs must be text-based (generated electronically), not scanned images. You can verify this by trying to select text in the PDF viewer.
2.  **File Size**: Maximum file size is 50MB.
3.  **Encryption**: PDFs must **not** be password protected. Please remove passwords before processing.
4.  **Structure**: Transactions should be presented in a tabular format with clear headers (Date, Description, Amount, etc.).

## Limitations

*   **Scanned Documents**: OCR is currently disabled for performance reasons. Scanned documents will likely fail or yield empty results.
*   **Complex Layouts**: Statements with multiple columns of text mixed with tables might require manual verification.
*   **Handwritten Notes**: Handwritten text on statements will be ignored.
