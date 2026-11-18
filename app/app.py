import json
import os
import shutil
from io import BytesIO

import fitz
import pytesseract
import streamlit as st
from PIL import Image, ImageEnhance, ImageOps


# Windows installers do not always add Tesseract to PATH. Allow an explicit
# override, then check the standard install locations before using PATH.
tesseract_cmd = os.environ.get("TESSERACT_CMD") or shutil.which("tesseract")
if not tesseract_cmd:
    for candidate in (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ):
        if os.path.isfile(candidate):
            tesseract_cmd = candidate
            break
if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


def extract_image_text(image):
    """Try enhanced versions and page layouts, then return the best OCR text."""
    gray = ImageOps.autocontrast(image.convert("L"))
    size = (gray.width * 2, gray.height * 2)
    enlarged = gray.resize(size, Image.Resampling.LANCZOS)
    sharpened = ImageEnhance.Sharpness(enlarged).enhance(2.0)
    variants = [sharpened]
    for threshold in (155, 185):
        variants.append(sharpened.point(lambda pixel, limit=threshold: 255 if pixel > limit else 0))

    best_text = ""
    best_confidence = -1.0
    for variant in variants:
        for page_mode in (6, 11):
            config = f"--oem 1 --psm {page_mode}"
            data = pytesseract.image_to_data(
                variant,
                config=config,
                output_type=pytesseract.Output.DICT,
            )
            text = pytesseract.image_to_string(variant, config=config).strip()
            words = [
                (word.strip(), float(confidence))
                for word, confidence in zip(data["text"], data["conf"])
                if word.strip() and float(confidence) >= 0
            ]
            if not words:
                continue
            confidence = sum(score for _, score in words) / len(words)
            if confidence > best_confidence:
                best_confidence = confidence
                best_text = text

    return best_text, (round(best_confidence, 1) if best_confidence >= 0 else 0.0)


def classify_document(text):
    normalized = text.casefold()
    if any(marker in normalized for marker in ("quick guide", "common medicines", "medicine guide", "list of medicines")):
        return "medicine_reference"
    lab_markers = ("reference range", "hemoglobin", "creatinine", "platelets", "wbc", "lab report")
    if sum(marker in normalized for marker in lab_markers) >= 2:
        return "lab_report"
    prescription_markers = ("prescription", "patient:", "frequency:", "duration:", "dose:")
    if sum(marker in normalized for marker in prescription_markers) >= 2:
        return "prescription"
    return "unknown"


st.set_page_config(
    page_title="TheCarePal AI Reader",
    page_icon="🏥",
    layout="wide",
)

st.title("🏥 TheCarePal - AI Prescription & Lab Reader")
st.write("Upload a prescription or laboratory report to extract its text.")
st.warning(
    "This tool does not diagnose medical conditions or replace professional "
    "medical judgement. Always verify extracted information."
)

uploaded_file = st.file_uploader(
    "Upload prescription or lab report",
    type=["png", "jpg", "jpeg", "pdf"],
)

if uploaded_file:
    confidence = None
    try:
        file_bytes = uploaded_file.getvalue()

        if uploaded_file.name.lower().endswith(".pdf"):
            extracted_pages = []
            with fitz.open(stream=file_bytes, filetype="pdf") as document:
                for page in document:
                    page_text = page.get_text("text").strip()
                    if not page_text:
                        pixmap = page.get_pixmap(dpi=250, alpha=False)
                        image = Image.open(BytesIO(pixmap.tobytes("png"))).convert("RGB")
                        page_text, confidence = extract_image_text(image)
                    extracted_pages.append(page_text)
            text = "\n\n".join(extracted_pages)
        else:
            image = Image.open(BytesIO(file_bytes)).convert("RGB")
            text, confidence = extract_image_text(image)
    except pytesseract.TesseractNotFoundError:
        st.error("Tesseract OCR is not installed or is not on PATH. Install it and restart the app.")
        st.stop()
    except pytesseract.TesseractError as error:
        st.error(f"Tesseract could not process this image: {error}")
        st.stop()
    except (fitz.FileDataError, OSError, ValueError) as error:
        st.error(f"Could not read this file: {error}")
        st.stop()

    st.subheader("Extracted Text")
    if confidence is not None:
        st.caption(f"Tesseract token confidence: {confidence}% — this measures OCR certainty, not whether the words are correct.")
        if confidence < 70:
            st.warning("OCR confidence is low. Handwriting may be misread; check every name and dose against the original.")
    corrected_text = st.text_area(
        "Review and correct extracted text",
        value=text,
        height=250,
    )
    st.download_button(
        "Download Text",
        corrected_text,
        file_name="extracted_text.txt",
        mime="text/plain",
    )

    document_type = st.selectbox(
        "Document type",
        options=["Auto-detect", "Prescription", "Lab report", "Medicine reference / guide", "Other / unknown"],
    )
    detected_type = classify_document(corrected_text)
    type_labels = {
        "prescription": "Prescription",
        "lab_report": "Lab report",
        "medicine_reference": "Medicine reference / guide",
        "unknown": "Other / unknown",
    }
    final_document_type = type_labels[detected_type] if document_type == "Auto-detect" else document_type
    st.caption(f"Document type: {final_document_type}")
    if detected_type == "medicine_reference" and document_type == "Auto-detect":
        st.info(
            "This looks like a general medicine guide, not an individual prescription. "
            "The app returns OCR text only; it does not turn a reference list into prescribed medicines."
        )
    result = {
        "document_type": final_document_type,
        "document_type_source": "automatic" if document_type == "Auto-detect" else "user_selected",
        "review_status": "manual_review_required",
        "tesseract_token_confidence_percent": confidence,
        "extracted_text": corrected_text,
    }

    st.subheader("JSON Output")
    st.caption(
        "This JSON contains the OCR text and its review metadata. "
        "Medicine and lab fields are not parsed yet."
    )
    formatted_json = json.dumps(result, indent=2, ensure_ascii=False)
    st.code(formatted_json, language="json", wrap_lines=True)
    st.download_button(
        "Download JSON",
        formatted_json,
        file_name="extracted_result.json",
        mime="application/json",
    )
