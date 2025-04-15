import os
import cv2
import numpy as np
import pytesseract
import pandas as pd
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
import spacy
from PIL import Image
import pillow_heif

# Import the entity extraction function
from entity_extraction import extract_entities

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
IMG_SIZE = (128, 128)
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Bert\Documents\Tesseract\tesseract.exe"

# Load trained models
handwritten_model = load_model("Trained Models\handwritten_cnn_lstm.h5")
printed_model = load_model("Trained Models\printed_train.h5")
print("Loaded both OCR models.")

# Load SpaCy NER model
nlp = spacy.load("en_core_web_sm")

def preprocess_image(image_path):
    try:
        # Try to read the image using OpenCV
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            # If OpenCV fails, try to open with PIL and convert to a format that OpenCV can read
            pil_image = Image.open(image_path).convert("L")  # Convert to grayscale
            img = np.array(pil_image)

        # Check if the image was successfully loaded
        if img is None or img.size == 0:
            raise ValueError(f"Failed to load image: {image_path}")

        img = cv2.resize(img, IMG_SIZE)
        img = img / 255.0  # Normalize
        img = img.reshape(1, IMG_SIZE[0], IMG_SIZE[1], 1)
        return img
    except Exception as e:
        print(f"Error processing image: {e}")
        return np.zeros((1, IMG_SIZE[0], IMG_SIZE[1], 1))  # Return a blank image to prevent crashing

def classify_receipt_type(image_path):
    """Classify receipt type (handwritten or printed) based on image characteristics."""
    img = preprocess_image(image_path)
    avg_pixel_value = np.mean(img)
    return "handwritten" if avg_pixel_value < 0.5 else "printed"

def convert_heic_to_jpg(input_path):
    """Convert HEIC to JPG using Pillow-HEIF."""
    try:
        # Register HEIF plugin
        pillow_heif.register_heif_opener()

        # Open HEIC file
        image = Image.open(input_path)

        # Convert to JPEG and save
        output_path = input_path.rsplit('.', 1)[0] + ".jpg"
        image = image.convert("RGB")
        image.save(output_path, "JPEG")
        print(f"Converted HEIC to JPEG: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error converting HEIC to JPG: {e}")
        return None

def perform_ocr(image_path, receipt_type):
    try:
        # Check if the file is HEIC and convert it to JPG if necessary
        if image_path.lower().endswith('.heic'):
            jpeg_path = convert_heic_to_jpg(image_path)
            if jpeg_path:
                image_path = jpeg_path
            else:
                print("Failed to convert HEIC to JPG.")
                return []

        # Open the image for OCR
        image = Image.open(image_path)
        config = '--oem 1 --psm 6' if receipt_type == "handwritten" else '--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, config=config)

        print("\nExtracted Text:")
        print("=" * 50)
        print(text)
        print("=" * 50)

        structured_text = text.strip().split("\n")
        return structured_text
    except Exception as e:
        print(f"Error performing OCR: {e}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    # Acceptable image extensions
    allowed_extensions = {'jpg', 'jpeg', 'png', 'heic', 'bmp', 'tiff', 'gif'}
    filename = secure_filename(file.filename)

    # Check if the file extension is allowed
    if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'error': f'Unsupported file type. Allowed types: {", ".join(allowed_extensions)}'})

    # Save the uploaded file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Classify receipt type
    receipt_type = classify_receipt_type(filepath)

    # Perform OCR
    ocr_result = perform_ocr(filepath, receipt_type)

    # Extract entities using NER and Pandas
    entities = extract_entities(ocr_result)

    return jsonify({
        'receipt_type': receipt_type,
        'ocr_result': ocr_result,
        'processed_image': filepath,
        'extracted_entities': entities
    })

if __name__ == '__main__':
    app.run(debug=True)
