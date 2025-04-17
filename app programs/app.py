import os
from flask import Flask, send_from_directory, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
from entity_extraction import extract_entities
import base64
import io

# Initialize Flask app
app = Flask(__name__)

# Base directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))
MAIN_DIR = os.path.join(BASE_DIR, 'Main')
NEW_DIR = os.path.join(BASE_DIR, 'New Record')
EXISTING_DIR = os.path.join(BASE_DIR, 'Existing Record')

# Static folder for uploaded files
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set up the Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Bert\Documents\Tesseract\tesseract.exe"

# === HTML ROUTES ===
@app.route('/')
def index():
    return send_from_directory(MAIN_DIR, 'main.html')

@app.route('/New/main.html')
def new_record():
    return send_from_directory(NEW_DIR, 'main.html')

@app.route('/Existing/main.html')
def existing_record():
    return send_from_directory(EXISTING_DIR, 'main.html')


# === STATIC ROUTES (CSS/JS) ===
@app.route('/Main/<path:filename>')
def main_static(filename):
    return send_from_directory(MAIN_DIR, filename)

@app.route('/New/<path:filename>')
def new_static(filename):
    return send_from_directory(NEW_DIR, filename)

@app.route('/Existing/<path:filename>')
def existing_static(filename):
    return send_from_directory(EXISTING_DIR, filename)


# === OCR Function ===
def perform_ocr(image_path):
    try:
        image = Image.open(image_path)
        # Preprocess the image: Convert to grayscale
        image = image.convert('L')

        # Optional: Apply other preprocessing steps like resizing or thresholding
        # image = image.resize((800, 600))  # Example: resize image to standard dimension
        # image = image.point(lambda p: p > 128 and 255)  # Apply thresholding

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


# === OCR and Entity Extraction Routes ===

# OCR with base64 image for live capture
@app.route('/process_receipt', methods=['POST'])
def process_receipt():
    data = request.get_json()
    image_data = data.get('image')

    if not image_data:
        return jsonify({'error': 'No image provided'}), 400

    try:
        # Decode the base64 image data
        header, encoded = image_data.split(",", 1)
        decoded_bytes = base64.b64decode(encoded)
        image = Image.open(io.BytesIO(decoded_bytes))

        # Perform OCR on the image
        ocr_result = pytesseract.image_to_string(image, config='--oem 3 --psm 6')
        ocr_result_lines = ocr_result.strip().split("\n")

        print("\nExtracted Text from Base64 Image:")
        print("=" * 50)
        print(ocr_result)
        print("=" * 50)

        # Extract entities from OCR result
        entities = extract_entities(ocr_result_lines)

        return jsonify({
            'ocr_result': ocr_result_lines,
            'extracted_entities': entities
        })

    except Exception as e:
        print(f"Error processing receipt: {e}")
        return jsonify({'error': str(e)}), 500


# === Run the app ===
if __name__ == '__main__':
    app.run(debug=True)
