import re
import spacy
import pandas as pd

# Load SpaCy NER model
nlp = spacy.load("en_core_web_sm")

def extract_entities(ocr_text):
    """Extract entities from OCR text and store them in a Pandas DataFrame."""
    ocr_text_lower = " ".join(ocr_text).lower()
    doc = nlp(ocr_text_lower)

    # Dictionary to store extracted entities (one per type)
    extracted_data = {
        "DATE": None,
        "OR NO": None,
        "AMOUNT": None,
        "VAT COMPANY": None,
        "INPUT VAT": None,
        "VAT REG TIN": None,
        "CASHIER": None,
        "TOTAL": None
    }

    # Enhanced regex patterns for better detection
    date_pattern = r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b"  # e.g., 3/14/25, 15/01/2019
    or_no_pattern = r"\bOR\s?NO[:\-]?\s?(\d+)"
    amount_pattern = r"\b(?:php|₱)?\s?(\d{1,3}(?:[.,]\d{3})*(?:\.\d{2})?)"
    vat_company_pattern = r"\b(VAT\s?COMPANY[:\-]?\s?[A-Za-z\s]+)"
    input_vat_pattern = r"\b(INPUT\s?VAT[:\-]?\s?[A-Za-z\s]+)"
    vat_tin_pattern = r"\b(VAT\s?REG\s?TIN[:\-]?\s?\d{3}[-\s]?\d{3}[-\s]?\d{3})"
    cashier_pattern = r"cashier\s?[:\-]?\s?([a-z\s]+)"
    
    # Multiple patterns to capture total amount correctly
    total_patterns = [
        r"\btotal\s?[:\-]?\s?(?:php|₱)?\s?(\d{1,3}(?:[.,]\d{3})*(?:\.\d{2})?)",
        r"\btotal\s+(?:php|₱)?\s?(\d{1,3}(?:[.,]\d{3})*(?:\.\d{2})?)",
        r"\btotal\W+(?:php|₱)?\s?(\d{1,3}(?:[.,]\d{3})*(?:\.\d{2})?)",
        r"\btotal\W+(?:php|₱)?\s?(\d+\.?\d*)",
        r"total\s+(?:php|₱)?\s?(\d+\.?\d*)"
    ]

    patterns = {
        "DATE": date_pattern,
        "OR NO": or_no_pattern,
        "AMOUNT": amount_pattern,
        "VAT COMPANY": vat_company_pattern,
        "INPUT VAT": input_vat_pattern,
        "VAT REG TIN": vat_tin_pattern,
        "CASHIER": cashier_pattern
    }

    # Search for each entity with the best possible pattern
    for key, pattern in patterns.items():
        match = re.search(pattern, ocr_text_lower)
        if match:
            extracted_data[key] = match.group(0)

    # Try multiple patterns to find the total amount
    for total_pattern in total_patterns:
        match = re.search(total_pattern, ocr_text_lower)
        if match:
            extracted_data["TOTAL"] = match.group(0)
            break

    # Use SpaCy NER to detect money entities as a fallback
    for ent in doc.ents:
        if ent.label_ == "MONEY" and not extracted_data["AMOUNT"]:
            extracted_data["AMOUNT"] = ent.text

    # Convert to DataFrame for displaying
    data_list = [{"Entity": key, "Value": value if value else "N/A"} for key, value in extracted_data.items()]
    return data_list
