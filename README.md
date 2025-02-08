# OCR-Based Patient Assessment Form Processing

## 📌 Project Overview

This project automates the extraction of data from patient assessment forms using Optical Character Recognition (OCR). It processes handwritten and printed forms, extracts structured data, and stores it in an SQLite database.

## 🔧 Features

- Uses **Tesseract OCR** and **EasyOCR** for text recognition.
- Extracts patient details, pain levels, and functional assessment data.
- Converts extracted data into **JSON format**.
- Stores structured data in an **SQLite database**.
- Includes an **interactive query mode** to search for specific patients.

## 📂 Project Structure

```
OCR-Patient-Assessment/
│── data/                 # Folder for sample images and JSON outputs
│   ├── sample_form.jpg
│   ├── output_tesseract.json
│   ├── output_easyocr.json
│── database/             # Folder for database storage
│   ├── ocr_results.db
│── scripts/              # Folder for Python scripts
│   ├── ocrwithinteractive.py  # Main OCR script with interactive features
│   ├── query_test.py          # Query testing script
│── README.md             # Documentation
│── requirements.txt      # List of dependencies
│── .gitignore            # Ignore unnecessary files
```

## 📥 Installation

### 1️⃣ Clone the Repository

```sh
git clone https://github.com/yourusername/OCR-Patient-Assessment.git
cd OCR-Patient-Assessment
```

### 2️⃣ Install Dependencies

```sh
pip install -r requirements.txt
```

## 🚀 Usage

### Running OCR on a Form

To extract data from an image:

```sh
python scripts/ocrwithinteractive.py data/sample_form.jpg
```

This will:

- Extract text from the image
- Store structured data in **JSON** and the **database**

### Running Interactive Queries

To enter the database query mode:

```sh
python scripts/ocrwithinteractive.py --query
```

You can:

1. View all records
2. Find patients with pain above a threshold
3. Find patients with difficulty in specific tasks

### Running a Query from a Script

To filter records where pain > 5, create a script:

```python
from ocrwithinteractive import query_database_interactive
query_database_interactive("database/ocr_results.db")
```

Run it:

```sh
python scripts/query_test.py
```

## 🛑 .gitignore File
To prevent unnecessary files from being tracked in Git, the `.gitignore` file includes:

```
__pycache__/
*.pyc
*.log
*.db
.DS_Store
```

This ensures that compiled Python files, logs, and the database file do not get committed to the repository.

## 📜 License

This project is open-source under the **MIT License**.

## 🤝 Contributing

Feel free to fork and submit pull requests. Let's improve the project together!

## 📝 Author

**Rohan Anvekar**\
GitHub: Rohan98-beep

