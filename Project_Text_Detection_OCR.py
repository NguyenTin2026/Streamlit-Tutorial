import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
from langdetect import detect
import platform
import os

# ===============================
# ⚙️ Cấu hình Tesseract OCR tự động theo OS
# ===============================
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    poppler_path = r"C:\poppler-23.12.0\bin"   # Sửa theo nơi bạn cài Poppler
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
    poppler_path = None

custom_config = r'--oem 3 --psm 6'

# ===============================
# 🖼️ Giao diện Streamlit
# ===============================
st.set_page_config(page_title="Smart OCR Premium", page_icon="🧠", layout="wide")

st.title("🧠 Smart OCR Pro - Vietnamese + English Text Recognition")
st.markdown("""
Ứng dụng OCR chuyên nghiệp dùng **Tesseract + Streamlit**  
Hỗ trợ ảnh, PDF, song ngữ (🇻🇳 + 🇺🇸), xuất văn bản và bounding box.
""")

uploaded_file = st.file_uploader("📤 Tải ảnh hoặc PDF", type=["png", "jpg", "jpeg", "pdf"])


# ===============================
# 🔍 Hàm OCR chính
# ===============================
@st.cache_resource
def ocr_process(image_np, lang):
    gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    gray = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 2
    )

    hImg, wImg = gray.shape
    boxes = pytesseract.image_to_boxes(gray, config=custom_config, lang=lang)
    img_copy = image_np.copy()

    for b in boxes.splitlines():
        b = b.split(' ')
        if len(b) >= 5:
            x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
            cv2.rectangle(img_copy, (x, hImg - y), (w, hImg - h), (0, 255, 0), 2)
            cv2.putText(img_copy, b[0], (x, hImg - y + 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    text = pytesseract.image_to_string(gray, config=custom_config, lang=lang)
    return img_copy, text


# ===============================
# 🔍 Xử lý file upload
# ===============================
if uploaded_file is not None:
    st.subheader("📄 Kết quả OCR:")

    # PDF
    if uploaded_file.name.lower().endswith(".pdf"):
        pages = convert_from_bytes(uploaded_file.read(), poppler_path=poppler_path)

        for i, page in enumerate(pages):
            st.write(f"### Trang {i+1}")

            img_np = np.array(page)
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

            # Phát hiện ngôn ngữ
            sample_text = pytesseract.image_to_string(img_bgr, config=custom_config, lang="vie+eng")
            try:
                lang_detected = detect(sample_text)
                lang = "vie" if lang_detected == "vi" else "eng"
            except:
                lang = "vie+eng"

            result_img, result_text = ocr_process(img_bgr, lang)

            st.image(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB),
                     caption=f"OCR Trang {i+1}", use_container_width=True)
            st.text_area(f"📘 Văn bản Trang {i+1}", result_text, height=200)

    # Ảnh
    else:
        image = Image.open(uploaded_file)
        img_np = np.array(image)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # Phát hiện ngôn ngữ
        sample_text = pytesseract.image_to_string(img_bgr, config=custom_config, lang="vie+eng")
        try:
            lang_detected = detect(sample_text)
            lang = "vie" if lang_detected == "vi" else "eng"
        except:
            lang = "vie+eng"

        result_img, result_text = ocr_process(img_bgr, lang)

        st.image(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB),
                 caption="Ảnh OCR", use_container_width=True)
        st.text_area("📘 Văn bản nhận dạng được", result_text, height=250)

        st.download_button(
            "📥 Tải kết quả OCR (.txt)",
            data=result_text,
            file_name="ocr_output.txt",
            mime="text/plain"
        )

else:
    st.info("⬆️ Tải lên ảnh hoặc PDF để bắt đầu nhận dạng.")
