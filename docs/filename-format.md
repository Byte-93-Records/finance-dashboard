# Bank and Card Name Parsing - Quick Guide

## How It Works

The system automatically extracts bank and card names from your PDF/CSV filenames.

### Filename Format

Name your files like this:
```
bankname_creditcardname_number_month_year.pdf
```

**Examples:**
- `chase_freedom_03_2025.pdf` → Bank: **Chase**, Card: **Freedom**
- `amex_platinum_04_2025.pdf` → Bank: **Amex**, Card: **Platinum**
- `bofa_cashrewards_12_2024.pdf` → Bank: **Bofa**, Card: **Cashrewards**

### What Gets Extracted

- **Bank Name**: First part (capitalized automatically)
- **Card Name**: Second part (capitalized automatically)
- **Month**: Third from end (optional, for reference)
- **Year**: Second from end (optional, for reference)

### Database Storage

This information is stored in the `accounts` table:
- `bank_name`: e.g., "Chase"
- `card_name`: e.g., "Freedom"  
- `name`: Combined, e.g., "Chase Freedom"
- `institution`: Same as bank_name

### Viewing in Grafana

You can now filter and group by:
- Bank Name
- Card Name
- Account Name (combination of both)

### Example Workflow

1. **Name your PDF:**
   ```bash
   mv statement.pdf chase_sapphire_03_2025.pdf
   ```

2. **Place in data/pdfs/:**
   ```bash
   cp chase_sapphire_03_2025.pdf data/pdfs/
   ```

3. **Run the pipeline:**
   ```bash
   ./scripts/process-and-view.sh
   ```

4. **Result in database:**
   - Account created: "Chase Sapphire"
   - Bank: Chase
   - Card: Sapphire

## Tips

- Use underscores (`_`) to separate parts
- Keep names simple (one word each if possible)
- The system capitalizes automatically, so `chase` becomes `Chase`
- Multiple word names work: `bank_of_america` becomes `Bank Of America`
