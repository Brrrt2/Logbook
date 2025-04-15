import cv2
import numpy as np
import pytesseract
import re
import spacy

# Configure the Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Bert\Documents\Tesseract\tesseract.exe"

# Load the pre-trained EAST text detector model from OpenCV
east_model_path = "frozen_east_text_detection.pb"
net = cv2.dnn.readNet(east_model_path)

# Load the SpaCy language model
nlp = spacy.load("en_core_web_sm")

def detect_text_east(image_path):
    # Load the image
    image = cv2.imread(image_path)
    orig = image.copy()
    (H, W) = image.shape[:2]

    # Resize image to multiple of 32 (EAST requirement)
    newW, newH = (320, 320)
    rW = W / float(newW)
    rH = H / float(newH)
    image = cv2.resize(image, (newW, newH))

    # Create a blob from the image
    blob = cv2.dnn.blobFromImage(image, 1.0, (newW, newH), (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net.setInput(blob)

    # Forward pass to get the scores and geometry
    (scores, geometry) = net.forward(['feature_fusion/Conv_7/Sigmoid', 'feature_fusion/concat_3'])
    (rects, confidences) = decode_predictions(scores, geometry)

    boxes = cv2.dnn.NMSBoxes(rects, confidences, 0.5, 0.4)
    extracted_texts = []

    for i in boxes.flatten():
        (x, y, w, h) = rects[i]
        startX = int(x * rW)
        startY = int(y * rH)
        endX = int((x + w) * rW)
        endY = int((y + h) * rH)

        # Extract the ROI
        roi = orig[startY:endY, startX:endX]
        text = pytesseract.image_to_string(roi, config="--psm 6").strip()

        if text:
            extracted_texts.append(text)
            cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)
            cv2.putText(orig, text, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Save the output image with bounding boxes
    output_path = "detected_text.jpg"
    cv2.imwrite(output_path, orig)
    print(f"\nOutput image saved to {output_path}")

    # Combine all texts into one string for NER processing
    combined_text = " ".join(extracted_texts)
    print("\n=== All Extracted Text ===")
    print(combined_text)
    
    # Extract useful information using NER and regex
    extract_relevant_info(combined_text)

def extract_relevant_info(text):
    # Extract amount using regex
    amount = re.findall(r"\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\b", text)
    date = re.findall(r"\b(?:\d{1,2}[/-])?\d{1,2}[/-]\d{2,4}\b", text)
    time = re.findall(r"\b\d{1,2}:\d{2}(?::\d{2})?\s?(?:AM|PM|am|pm)?\b", text)
    
    # Use Spacy to extract organization names (store names)
    doc = nlp(text)
    company_names = [ent.text for ent in doc.ents if ent.label_ == "ORG"]

    print("\n=== Extracted Information ===")
    print(f"Company Name: {company_names[0] if company_names else 'N/A'}")
    print(f"Total Amount: {amount[-1] if amount else 'N/A'}")
    print(f"Date: {date[-1] if date else 'N/A'}")
    print(f"Time: {time[-1] if time else 'N/A'}")

def decode_predictions(scores, geometry):
    numRows, numCols = scores.shape[2:4]
    rects = []
    confidences = []

    for y in range(numRows):
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        for x in range(numCols):
            score = scoresData[x]
            if score < 0.5:
                continue

            offsetX, offsetY = (x * 4.0), (y * 4.0)
            angle = anglesData[x]
            cos, sin = np.cos(angle), np.sin(angle)
            h, w = xData0[x] + xData2[x], xData1[x] + xData3[x]
            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX, startY = int(endX - w), int(endY - h)

            rects.append((startX, startY, w, h))
            confidences.append(float(score))

    return (rects, confidences)

# Run the function with a sample receipt image
detect_text_east("IMG_1761.jpg")
