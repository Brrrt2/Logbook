import re
import spacy
import pandas as pd

# Load SpaCy NER model
nlp = spacy.load("en_core_web_sm")

def extract_entities(ocr_text):
    """Extract entities from OCR text and store them in a list of dictionaries."""
    ocr_text_lower = " ".join(ocr_text).lower()
    doc = nlp(ocr_text_lower)

    extracted_data = {
        "DATE": None,
        "DESCRIPTION": None,
        "AMOUNT": None,
        "INVOICE NUMBER": None,
        "VAT COMPANY": None,
        "INPUT TAX AMOUNT": None,
        "VAT REGISTRATION TIN": None
    }

    # Regex patterns
    # Modified Regex patterns based on your initial request
    date_pattern = r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b"
    amount_pattern = r"\b(?:php|₱)?\s?(\d{1,3}(?:[.,]\d{3})*(?:\.\d{2})?)"
    invoice_pattern = r"S\.I\. #:\s*(\d+)"
    vat_company_pattern = r"VAT REG TIN:\s*(\d{3}-\d{3}-\d{3})"
    input_tax_pattern = r"VAT Amount\s*(Php[\d,]+\.\d{2})" # Assuming "Input Tax" refers to "VAT Amount" in this context
    vat_tin_pattern = r"VAT REG TIN:\s*(\d{3}-\d{3}-\d{3})"

    patterns = {
        "DATE": date_pattern,
        "AMOUNT": amount_pattern,
        "INVOICE NUMBER": invoice_pattern,
        "VAT COMPANY": vat_company_pattern,
        "INPUT TAX AMOUNT": input_tax_pattern,
        "VAT REGISTRATION TIN": vat_tin_pattern
    }

    # Apply regex search
    for key, pattern in patterns.items():
        match = re.search(pattern, ocr_text_lower)
        if match:
            extracted_data[key] = match.group(0)

    # Try to extract DESCRIPTION line
    lines = ocr_text_lower.split('\n')
    for line in lines:
        if "description" in line:
            match = re.search(r"description[:\-]?\s?(.*)", line)
            if match:
                extracted_data["DESCRIPTION"] = match.group(1).strip()
                break

    # Fallback with SpaCy NER
    for ent in doc.ents:
        if ent.label_ == "MONEY" and not extracted_data["AMOUNT"]:
            extracted_data["AMOUNT"] = ent.text

    # Prepare results
    result = [{"Entity": key, "Value": value if value else "N/A"} for key, value in extracted_data.items()]

    # 🔽 Print extracted entities
    print("\nExtracted Entities:")
    print("=" * 40)
    for item in result:
        print(f"{item['Entity']}: {item['Value']}")
    print("=" * 40)

    return result

