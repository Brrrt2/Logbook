import cv2
import numpy as np
from PIL import Image

def preprocess_image(image_path):
    # Load image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Denoise the image
    img = cv2.fastNlMeansDenoising(img, h=30)

    # Apply adaptive thresholding
    img = cv2.adaptiveThreshold(
        img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 10
    )

    # Resize to enhance small text
    scale_percent = 150  # Resize by 150%
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    img = cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)

    # Convert OpenCV image to PIL format for Tesseract
    return Image.fromarray(img)
