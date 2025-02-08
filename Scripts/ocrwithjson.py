import cv2
import pytesseract
import easyocr
import sqlite3
import numpy as np
import argparse
import re
import json
import os

# Set Tesseract path (Only for Windows, change accordingly)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image_path):
    """Preprocess the image for better OCR accuracy."""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale

    # Apply simple thresholding for binarization
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

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
    data["dob"] = re.search(r"DOB:\s*(\d{1,2}/\d{1,2}/\d{2,4})", text).group(1) if re.search(r"DOB:\s*(\d{1,2}/\d{1,2}/\d{2,4})", text) else "Unknown"
    
    # Extract Treatment Details
    data["date"] = re.search(r"Date:\s*(\d{1,2}/\d{1,2}/\d{2,4})", text).group(1) if re.search(r"Date:\s*(\d{1,2}/\d{1,2}/\d{2,4})", text) else "Unknown"
    data["injection"] = "Yes" if re.search(r"INJECTION:\s*YES", text, re.IGNORECASE) else "No"
    data["exercise_therapy"] = "Yes" if re.search(r"Exercise Therapy:\s*YES", text, re.IGNORECASE) else "No"
    
    # Extract Pain Symptoms
    data["pain_symptoms"] = {
        "pain": int(re.search(r"Pain:\s*(\d+)", text).group(1)) if re.search(r"Pain:\s*(\d+)", text) else 0,
        "numbness": int(re.search(r"Numbness:\s*(\d+)", text).group(1)) if re.search(r"Numbness:\s*(\d+)", text) else 0,
        "tingling": int(re.search(r"Tingling:\s*(\d+)", text).group(1)) if re.search(r"Tingling:\s*(\d+)", text) else 0,
        "burning": int(re.search(r"Burning:\s*(\d+)", text).group(1)) if re.search(r"Burning:\s*(\d+)", text) else 0,
        "tightness": int(re.search(r"Tightness:\s*(\d+)", text).group(1)) if re.search(r"Tightness:\s*(\d+)", text) else 0
    }
    
    return data

def save_to_database(data, db_path="ocr_results.db"):
    """Save extracted data to an SQLite database."""
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ocr_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            dob TEXT,
            date TEXT,
            injection TEXT,
            exercise_therapy TEXT,
            pain INTEGER,
            numbness INTEGER,
            tingling INTEGER,
            burning INTEGER,
            tightness INTEGER
        )
    ''')

    # Insert data into table
    cursor.execute('''
        INSERT INTO ocr_results (
            patient_name, dob, date, injection, exercise_therapy, 
            pain, numbness, tingling, burning, tightness
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data["patient_name"], data["dob"], data["date"], data["injection"], data["exercise_therapy"], 
        data["pain_symptoms"]["pain"], data["pain_symptoms"]["numbness"], data["pain_symptoms"]["tingling"], 
        data["pain_symptoms"]["burning"], data["pain_symptoms"]["tightness"]
    ))

    connection.commit()
    connection.close()

def save_to_json(data, output_path):
    """Save structured data to a JSON file."""
    with open(output_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OCR Extraction from an Image")
    parser.add_argument("image_path", type=str, help="Path to the input image")
    args = parser.parse_args()
    
    image_path = args.image_path
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    print("Extracting with Tesseract OCR...")
    tesseract_text = extract_text_tesseract(image_path)
    print("Tesseract Output:\n", tesseract_text)
    structured_data = extract_key_data(tesseract_text)
    print("Structured Data (Tesseract):\n", json.dumps(structured_data, indent=4))

    print("Saving Tesseract OCR data to database...")
    save_to_database(structured_data)
    print("Data saved successfully.")

    tesseract_json_path = f"{base_name}_tesseract.json"
    print(f"Saving Tesseract OCR data to JSON: {tesseract_json_path}...")
    save_to_json(structured_data, tesseract_json_path)
    print("JSON saved successfully.")
    
    print("\nExtracting with EasyOCR...")
    easyocr_text = extract_text_easyocr(image_path)
    print("EasyOCR Output:\n", easyocr_text)
    structured_data_easyocr = extract_key_data(easyocr_text)
    print("Structured Data (EasyOCR):\n", json.dumps(structured_data_easyocr, indent=4))

    print("Saving EasyOCR data to database...")
    save_to_database(structured_data_easyocr)
    print("Data saved successfully.")

    easyocr_json_path = f"{base_name}_easyocr.json"
    print(f"Saving EasyOCR data to JSON: {easyocr_json_path}...")
    save_to_json(structured_data_easyocr, easyocr_json_path)
    print("JSON saved successfully.")
