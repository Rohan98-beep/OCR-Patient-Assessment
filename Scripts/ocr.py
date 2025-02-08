import cv2
print(cv2.__version__)
import pytesseract
print(pytesseract.__version__)
import easyocr
import numpy as np
import argparse
import re
import json

# Set Tesseract path (Only for Windows, change accordingly)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image_path):
    """Preprocess the image for better OCR accuracy."""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)  # Reduce noise
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)  # Binarization
    return thresh

def extract_text_tesseract(image_path):
    """Extract text using Tesseract OCR."""
    processed_image = preprocess_image(image_path)
    text = pytesseract.image_to_string(processed_image, config='--psm 6')
    return text

def extract_text_easyocr(image_path):
    """Extract text using EasyOCR."""
    reader = easyocr.Reader(['en'])  # Load English language model
    result = reader.readtext(image_path, detail=0)  # Extract text without details
    return '\n'.join(result)

def extract_key_data(text):
    """Extract structured data from OCR text using regex and string matching."""
    data = {}
    
    # Extract Patient Details
    data["patient_name"] = re.search(r"Patient Name:\s*(.*)", text, re.IGNORECASE).group(1) if re.search(r"Patient Name:\s*(.*)", text, re.IGNORECASE) else "Unknown"
    data["dob"] = re.search(r"DOB:\s*(\d{2}/\d{2}/\d{4})", text).group(1) if re.search(r"DOB:\s*(\d{2}/\d{2}/\d{4})", text) else "Unknown"
    
    # Extract Treatment Details
    data["date"] = re.search(r"Date:\s*(\d{2}/\d{2}/\d{4})", text).group(1) if re.search(r"Date:\s*(\d{2}/\d{2}/\d{4})", text) else "Unknown"
    data["injection"] = "Yes" if "INJECTION: YES" in text else "No"
    data["exercise_therapy"] = "Yes" if "Exercise Therapy: YES" in text else "No"
    
    # Extract Pain Symptoms
    data["pain_symptoms"] = {
        "pain": int(re.search(r"Pain:\s*(\d+)", text).group(1)) if re.search(r"Pain:\s*(\d+)", text) else 0,
        "numbness": int(re.search(r"Numbness:\s*(\d+)", text).group(1)) if re.search(r"Numbness:\s*(\d+)", text) else 0,
        "tingling": int(re.search(r"Tingling:\s*(\d+)", text).group(1)) if re.search(r"Tingling:\s*(\d+)", text) else 0,
        "burning": int(re.search(r"Burning:\s*(\d+)", text).group(1)) if re.search(r"Burning:\s*(\d+)", text) else 0,
        "tightness": int(re.search(r"Tightness:\s*(\d+)", text).group(1)) if re.search(r"Tightness:\s*(\d+)", text) else 0
    }
    
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OCR Extraction from an Image")
    parser.add_argument("image_path", type=str, help="Path to the input image")
    args = parser.parse_args()
    
    image_path = args.image_path
    
    print("Extracting with Tesseract OCR...")
    tesseract_text = extract_text_tesseract(image_path)
    structured_data = extract_key_data(tesseract_text)
    print(json.dumps(structured_data, indent=4))
    
    print("\nExtracting with EasyOCR...")
    easyocr_text = extract_text_easyocr(image_path)
    structured_data_easyocr = extract_key_data(easyocr_text)
    print(json.dumps(structured_data_easyocr, indent=4))
