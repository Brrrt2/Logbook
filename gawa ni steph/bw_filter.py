import cv2
import numpy as np
from matplotlib import pyplot as plt

# Load the image (using OpenCV sample image as placeholder)
image_path = "C:/Users/steph/Downloads/IMG_0161.jpg"
image = cv2.imread(image_path)

# Resize for display
image = cv2.resize(image, (2500, int(image.shape[0] * 2500 / image.shape[1]))) ## change accordingly. 

# Step 1: Perspective Correction
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(blurred, 75, 200)

# Find contours
contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

doc_contour = None
for c in contours:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    if len(approx) == 4:
        doc_contour = approx
        break

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def four_point_transform(image, pts):
    rect = order_points(pts.reshape(4, 2))
    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, M, (maxWidth, maxHeight))

# Apply transform
if doc_contour is not None:
    scanned = four_point_transform(image, doc_contour)
else:
    scanned = image.copy()

# Step 2: Black and White Filter (OCR-Ready)
gray_scan = cv2.cvtColor(scanned, cv2.COLOR_BGR2GRAY)
bw = cv2.adaptiveThreshold(gray_scan, 255,
                           cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                           cv2.THRESH_BINARY, 15, 10)

# # Step 3: Rotation Correction (deskewing)
# coords = np.column_stack(np.where(bw > 0))
# angle = cv2.minAreaRect(coords)[-1]
# if angle < -45:
#     angle = -(90 + angle)
# else:
#     angle = -angle

# (h, w) = bw.shape
# center = (w // 2, h // 2)
# M = cv2.getRotationMatrix2D(center, angle, 1.0)
# deskewed = cv2.warpAffine(bw, M, (w, h),
#                           flags=cv2.INTER_CUBIC,
#                           borderMode=cv2.BORDER_REPLICATE)

# Display outputs
plt.figure(figsize=(18, 6))
plt.subplot(1, 3, 1)
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
plt.title("Original")
plt.axis('off')

plt.subplot(1, 3, 2)
plt.imshow(bw, cmap='gray')
plt.title("Black & White (Thresholded)")
plt.axis('off')

plt.tight_layout()
plt.show()
