"""Helper functions for parsing bank and card information from filenames"""

def parse_filename(filename: str) -> dict:
    """
    Parse filename in format: bankname_creditcardname_number_month_year.pdf
    
    Example: chase_freedom_03_2025.pdf
    Returns: {'bank_name': 'chase', 'card_name': 'freedom', 'month': '03', 'year': '2025'}
    """
    # Remove file extension and path
    import os
    basename = os.path.basename(filename)
    name_without_ext = os.path.splitext(basename)[0]
    
    # Split by underscore
    parts = name_without_ext.split('_')
    
    result = {
        'bank_name': None,
        'card_name': None,
        'month': None,
        'year': None
    }
    
    if len(parts) >= 2:
        result['bank_name'] = parts[0].title()  # Capitalize: chase -> Chase
        result['card_name'] = parts[1].title()  # Capitalize: freedom -> Freedom
    
    if len(parts) >= 4:
        # Last two parts are typically month and year
        result['month'] = parts[-2]
        result['year'] = parts[-1]
    
    return result


if __name__ == "__main__":
    # Test cases
    test_files = [
        "chase_freedom_03_2025.pdf",
        "amex_platinum_04_2025.csv",
        "bofa_cashrewards_12_2024.pdf"
    ]
    
    for test_file in test_files:
        result = parse_filename(test_file)
        print(f"{test_file} -> {result}")
