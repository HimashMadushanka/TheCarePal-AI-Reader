# TheCarePal AI Reader

TheCarePal AI Reader is a learning project for extracting text from prescription and laboratory documents. It provides a Streamlit interface for image and PDF uploads, plus Jupyter notebooks that demonstrate document exploration, preprocessing, OCR, extraction, JSON output, evaluation, and confidence scoring.

> **Important:** This project is for educational use. It does not diagnose conditions or provide medical advice. Always verify OCR results and medicine instructions with a qualified healthcare professional.

## Features

- Upload PNG, JPG, and PDF documents.
- Read text embedded in PDFs directly and use Tesseract OCR for images or scanned PDF pages.
- Enhance images and try multiple OCR layouts to improve recognition.
- Review and edit extracted text before downloading it.
- Download the OCR result with document type and review metadata as JSON.
- Run the sample notebooks against the included fictional text data.

The app currently returns OCR text; it does **not** reliably extract structured medicine names, doses, schedules, or laboratory values. Document type detection is a best-effort label. Tesseract confidence is not a measure of medical accuracy, and handwritten notes may be misread.

## Requirements

- Python 3.10 or newer
- Tesseract OCR installed separately for image and scanned-PDF OCR

The Python wrapper (`pytesseract`) is installed from `requirements.txt`; it does not include the Tesseract OCR engine itself. The app checks `PATH` and the standard Windows installation locations. For a custom location, set `TESSERACT_CMD` to the full path of `tesseract.exe`.

## Setup on Windows

Run these commands from the project root in PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install Tesseract OCR separately, then start the app:

```powershell
python -m streamlit run app/app.py
```

If Tesseract is installed in a nonstandard location, configure it before starting Streamlit:

```powershell
$env:TESSERACT_CMD = "C:\Path\To\Tesseract-OCR\tesseract.exe"
python -m streamlit run app/app.py
```

Streamlit prints a local URL in the terminal when the app starts. Open that URL in a browser.

## Sample data

All supplied examples are fictional and contain no real patient records. The `.txt` samples are intended for extraction and evaluation work; image and PDF samples can be added later for OCR experiments.

```text
data/
├── prescriptions/
│   ├── prescription_01.txt
│   ├── prescription_02.txt
│   └── prescription_03.txt
├── lab_reports/
│   ├── lab_01.txt
│   ├── lab_02.txt
│   └── lab_03.txt
└── ground_truth/
    ├── medicines.json
    └── lab_values.json
```

## Notebooks

The notebooks in `notebooks/` cover these stages:

1. Data exploration
2. Image preprocessing
3. OCR extraction
4. Medicine extraction
5. Laboratory result extraction
6. JSON output
7. Model evaluation
8. OCR confidence scoring

Open them with Jupyter from the project root or the `notebooks/` directory. Image preprocessing and OCR confidence examples will prompt for image samples when none are present.

## Project structure

```text
app/app.py          Streamlit application
data/               Fictional sample documents and ground truth
notebooks/          Step-by-step extraction experiments
requirements.txt    Python dependencies
```
