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
        "AMOUNT_PESOS": None,
        "AMOUNT_CENTS": None,
        "INVOICE NUMBER": None,
        "VAT COMPANY": None,
        "INPUT TAX PESOS": None,
        "INPUT TAX CENTS": None,
        "VAT REGISTRATION TIN": None    
    }

    # Regex patterns
    date_pattern = r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b"
    # amount_pattern = r"\b(?:php|₱)?\s?(\d{1,3}(?:[.,]\d{3})*(?:\.\d{2})?)"
    amount_pattern = r"\b(?:php|₱)?\s*(\d{1,3}(?:[.,]\d{3})*|\d+)[.,](\d{2})\b"
    invoice_pattern = r"S\.I\. #:\s*(\d+)"
    vat_company_pattern = r"\b([A-Z][A-Za-z&.,'-]{2,}(?:\s+[A-Z][A-Za-z&.,'-]{2,}){1,5})\s+(?:Inc\.?|Corp\.?|Corporation|Ltd\.?|Enterprises|Incorporated|Company|VAT|TIN|REG|REG\.?|CO\.)" # 
    # input_tax_pattern = r"VAT Amount\s*(Php[\d,]+\.\d{2})"
    input_tax_pattern = r"VAT Amount\s*(?:Php|₱)?\s*(\d{1,3}(?:[.,]\d{3})*|\d+)[.,](\d{2})"
    vat_tin_pattern = r"VAT REG TIN:\s*(\d{3}-\d{3}-\d{3})"

    patterns = {
        "DATE": date_pattern,
        "AMOUNT": amount_pattern, ## remove later
        "INVOICE NUMBER": invoice_pattern,
        "VAT COMPANY": vat_company_pattern,
        "INPUT TAX AMOUNT": input_tax_pattern, ## remove, separate logic
        "VAT REGISTRATION TIN": vat_tin_pattern
    }

    # Apply regex search
    for key, pattern in patterns.items():
        match = re.search(pattern, ocr_text_lower)
        if match:
            extracted_data[key] = match.group(0)

    ## Amount -- reads pesos/cents separately
    match = re.search(amount_pattern, ocr_text_lower)
    if match:
        extracted_data["AMOUNT_PESOS"] = match.group(1).replace(",", "")
        extracted_data["AMOUNT_CENTS"] = match.group(2)
    
    ## Input Tax -- same thing
    match = re.search(input_tax_pattern, ocr_text_lower)
    if match:
        extracted_data["INPUT_TAX_PESOS"] = match.group(1).replace(",", "")
        extracted_data["INPUT_TAX_CENTS"] = match.group(2)
     

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
