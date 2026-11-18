
import streamlit as st
import pytesseract
import fitz
import cv2
import json

from PIL import Image
import numpy as np

st.set_page_config(
    page_title="TheCarePal AI Reader",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 TheCarePal - AI Prescription & Lab Reader")

st.write(
    "Upload a prescription or laboratory report "
    "to extract its text."
)

st.warning(
    "This tool does not diagnose medical conditions "
    "or replace professional medical judgement. "
    "Always verify extracted information."
)

uploaded_file = st.file_uploader(
    "Upload prescription or lab report",
    type=["png", "jpg", "jpeg", "pdf"]
)

if uploaded_file:

    file_bytes = uploaded_file.read()

    if uploaded_file.name.lower().endswith(".pdf"):

        doc = fitz.open(
            stream=file_bytes,
            filetype="pdf"
        )

        extracted_text = []

        for page in doc:

            pix = page.get_pixmap(dpi=250)

            image = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples
            )

            extracted_text.append(
                pytesseract.image_to_string(image)
            )

        doc.close()

        text = "\n".join(extracted_text)

    else:

        image = Image.open(uploaded_file).convert("RGB")

        text = pytesseract.image_to_string(image)

    st.subheader("Extracted Text")

    corrected_text = st.text_area(
        "Review and correct extracted text",
        value=text,
        height=250
    )

    if st.button("Save Extracted Text"):

        st.download_button(
            "Download Text",
            corrected_text,
            file_name="extracted_text.txt"
        )

    st.subheader("Extracted JSON")

    result = {
        "extracted_text": corrected_text
    }

    st.json(result)

    st.download_button(
        "Download JSON",
        json.dumps(result, indent=4),
        file_name="extracted_result.json",
        mime="application/json"
    )
