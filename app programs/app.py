import os
import base64
import io
import uuid
from flask import Flask, send_from_directory, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from ocr_scanner import perform_ocr  # Uses image path input
from entity_extraction import extract_entities
import pillow_heif
pillow_heif.register_heif_opener()

# Initialize Flask app
app = Flask(__name__)

# Base directory setup
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))
MAIN_DIR = os.path.join(BASE_DIR, 'Main')
NEW_DIR = os.path.join(BASE_DIR, 'New Record')
EXISTING_DIR = os.path.join(BASE_DIR, 'Existing Record')
ABOUTUS_DIR = os.path.join(BASE_DIR, 'About Us')

# Upload folder  Saves the uploaded images
# to a static/uploads directory
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

@app.route('/About_Us/main.html')
def aboutus_record():
    return send_from_directory(ABOUTUS_DIR, 'main.html')

# === STATIC FILES ===
@app.route('/Main/<path:filename>')
def main_static(filename):
    return send_from_directory(MAIN_DIR, filename)

@app.route('/New/<path:filename>')
def new_static(filename):
    return send_from_directory(NEW_DIR, filename)

@app.route('/Existing/<path:filename>')
def existing_static(filename):
    return send_from_directory(EXISTING_DIR, filename)

@app.route('/About Us/<path:filename>')
def aboutus_static(filename):
    return send_from_directory(ABOUTUS_DIR, filename)

# === OCR + ENTITY EXTRACTION ===
@app.route('/process_receipt', methods=['POST'])
def process_receipt():
    data = request.get_json()
    image_data = data.get('image')

    if not image_data:
        return jsonify({'error': 'No image provided'}), 400

    try:
        # Decode base64 image
        header, encoded = image_data.split(",", 1)
        decoded_bytes = base64.b64decode(encoded)

        # Read image and detect format
        image = Image.open(io.BytesIO(decoded_bytes))
        image_format = image.format.lower()

        # Convert HEIC to JPG if necessary
        if image_format == 'heic' or image.mode in ("RGBA", "P"):
            image = image.convert("RGB") # Convert to RGB for JPEG

        # Save as .jpg regardless of input format for compatibility
        filename = f"{uuid.uuid4().hex}.jpg"
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(temp_path, "JPEG")

        # Run OCR
        ocr_result_lines = perform_ocr(temp_path)

        # Extract entities
        entities = extract_entities(ocr_result_lines)

        # Optional: Delete temp image
        #os.remove(temp_path)

        return jsonify({
            'ocr_result': ocr_result_lines,
            'extracted_entities': entities
        })

    except Exception as e:
        print(f"Error processing receipt: {e}")
        return jsonify({'error': str(e)}), 500


# === RUN APP ===
if __name__ == '__main__':
    app.run(debug=True)
