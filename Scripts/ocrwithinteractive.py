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

def query_database_interactive(db_path="ocr_results.db"):
    """Allow the user to interactively query the database."""
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    while True:
        print("\nInteractive Database Query")
        print("1. Show all records")
        print("2. Find patients with pain level above a certain threshold")
        print("3. Find patients with high difficulty ratings")
        print("4. Exit query mode")
        
        choice = input("Enter choice: ")
        
        if choice == "1":
            query = "SELECT * FROM ocr_results"
        elif choice == "2":
            threshold = input("Enter pain level threshold: ")
            query = f"SELECT * FROM ocr_results WHERE pain > {threshold}"
        elif choice == "3":
            task = input("Enter task name (e.g., bending, sleeping): ").lower().replace(' ', '_')
            difficulty_level = input("Enter difficulty level threshold: ")
            query = f"SELECT * FROM ocr_results WHERE difficulty_ratings LIKE '%\"{task}\": {difficulty_level}%'"
        elif choice == "4":
            break
        else:
            print("Invalid choice. Try again.")
            continue
        
        cursor.execute(query)
        results = cursor.fetchall()
        print("\nQuery Results:")
        for row in results:
            print(row)
    
    connection.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OCR Extraction from an Image")
    parser.add_argument("image_path", type=str, help="Path to the input image")
    parser.add_argument("--query", action="store_true", help="Run interactive database query mode")
    args = parser.parse_args()
    
    if args.query:
        query_database_interactive()
    else:
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
