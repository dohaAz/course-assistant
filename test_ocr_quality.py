
from pathlib import Path
from io import BytesIO

import pymupdf
from PIL import Image, ImageOps, ImageEnhance
import pytesseract

# Windows Tesseract installation
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

pdf_path = Path("data/Gen-AI3.pdf")
doc = pymupdf.open(pdf_path)

# Test PDF page 5 (index 4)
page = doc[4]

# High-resolution rendering: 300 DPI
pix = page.get_pixmap(
    dpi=300,
    colorspace=pymupdf.csRGB,
    alpha=False
)

image = Image.open(BytesIO(pix.tobytes("png")))

# Improve contrast
gray = ImageOps.grayscale(image)
enhanced = ImageOps.autocontrast(gray)
enhanced = ImageEnhance.Sharpness(enhanced).enhance(1.5)

# OCR configuration A: standard
text_a = pytesseract.image_to_string(
    image,
    lang="eng",
    config="--oem 3 --psm 3"
)

# OCR configuration B: sparse slide layout
text_b = pytesseract.image_to_string(
    enhanced,
    lang="eng",
    config="--oem 3 --psm 11"
)

print("\n===== STANDARD OCR =====\n")
print(text_a[:2000])

print("\n===== IMPROVED OCR =====\n")
print(text_b[:2000])

doc.close()
