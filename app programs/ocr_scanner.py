import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Bert\Documents\Tesseract\tesseract.exe"

def perform_ocr(image_path):
    try:
        image = Image.open(image_path)
        config = '--oem 3 --psm 6'  # Assuming printed for now
        text = pytesseract.image_to_string(image, config=config)

        print("\nExtracted Text:")
        print("=" * 50)
        print(text)
        print("=" * 50)

        return text.strip().split("\n")
    except Exception as e:
        print(f"Error performing OCR: {e}")
        return []
