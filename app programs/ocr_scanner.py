import pytesseract
from PIL import Image
from image_processing import preprocess_image

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Bert\Documents\Tesseract\tesseract.exe"

def perform_ocr(image_path):
    try:
        preprocessed_img = preprocess_image(image_path)

        config = '--oem 3 --psm 6'  # OCR engine mode and page segmentation
        text = pytesseract.image_to_string(preprocessed_img, config=config)

        print("\nExtracted Text:")
        print("=" * 50)
        print(text)
        print("=" * 50)

        return text.strip().split("\n")
    except Exception as e:
        print(f"Error performing OCR: {e}")
        return []
