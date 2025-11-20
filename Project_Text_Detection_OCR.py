import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
from langdetect import detect
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> d426f62 (Initial commit on master)



# ===============================
# ⚙️ Cấu hình Tesseract OCR
# ===============================
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
<<<<<<< HEAD
=======
=======
import platform
import os

# ===============================
# ⚙️ Cấu hình Tesseract OCR tự động theo OS
# ===============================
if platform.system() == "Windows":
    # Windows local
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    poppler_path = r"C:\poppler-23.12.0\bin"  # Thay bằng đường dẫn Poppler của bạn
else:
    # Linux / Streamlit Cloud
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
    poppler_path = None

>>>>>>> 2ba32ab (update requirement.txt)
>>>>>>> d426f62 (Initial commit on master)
custom_config = r'--oem 3 --psm 6'

# ===============================
# 🖼️ Giao diện Streamlit
# ===============================
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> d426f62 (Initial commit on master)
st.set_page_config(page_title="Smart OCR Premium - Nguyen Tin Tin Do", page_icon="🧠", layout="wide")

st.title("🧠 Smart OCR Pro - Vietnamese + English Text Recognition")
st.markdown("""
Ứng dụng OCR chuyên nghiệp dùng **Tesseract + Streamlit**  
<<<<<<< HEAD
=======
=======
st.set_page_config(page_title="Smart OCR Premium", page_icon="🧠", layout="wide")
st.title("🧠 Smart OCR Pro - Vietnamese + English Text Recognition")
st.markdown("""
Ứng dụng OCR dùng **Tesseract + Streamlit**  
>>>>>>> 2ba32ab (update requirement.txt)
>>>>>>> d426f62 (Initial commit on master)
Hỗ trợ ảnh, PDF, song ngữ (🇻🇳 + 🇺🇸), xuất văn bản và bounding box.
""")

uploaded_file = st.file_uploader("📤 Tải ảnh hoặc PDF", type=["png", "jpg", "jpeg", "pdf"])

@st.cache_resource
def ocr_process(image_np, lang):
    gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 31, 2)
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> d426f62 (Initial commit on master)

    hImg, wImg = gray.shape
    boxes = pytesseract.image_to_boxes(gray, config=custom_config, lang=lang)
    img_copy = image_np.copy()

<<<<<<< HEAD
=======
=======
    hImg, wImg = gray.shape
    boxes = pytesseract.image_to_boxes(gray, config=custom_config, lang=lang)
    img_copy = image_np.copy()
>>>>>>> 2ba32ab (update requirement.txt)
>>>>>>> d426f62 (Initial commit on master)
    for b in boxes.splitlines():
        b = b.split(' ')
        if len(b) >= 5:
            x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
            cv2.rectangle(img_copy, (x, hImg - y), (w, hImg - h), (0, 255, 0), 2)
            cv2.putText(img_copy, b[0], (x, hImg - y + 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> d426f62 (Initial commit on master)

    text = pytesseract.image_to_string(gray, config=custom_config, lang=lang)
    return img_copy, text

if uploaded_file is not None:
    st.subheader("📄 Kết quả OCR:")

    # ===============================
    # 🔍 Xử lý PDF hoặc Ảnh
    # ===============================
    if uploaded_file.name.lower().endswith(".pdf"):
        # ✅ Thêm đường dẫn poppler
        poppler_path = r"C:\poppler-23.12.0\bin"  # <-- sửa theo nơi bạn giải nén Poppler
        pages = convert_from_bytes(uploaded_file.read(), poppler_path=poppler_path)

<<<<<<< HEAD
=======
=======
    text = pytesseract.image_to_string(gray, config=custom_config, lang=lang)
    return img_copy, text

# ===============================
# 🔍 Xử lý file upload
# ===============================
if uploaded_file is not None:
    st.subheader("📄 Kết quả OCR:")

    if uploaded_file.name.lower().endswith(".pdf"):
        pages = convert_from_bytes(uploaded_file.read(), poppler_path=poppler_path)
>>>>>>> 2ba32ab (update requirement.txt)
>>>>>>> d426f62 (Initial commit on master)
        for i, page in enumerate(pages):
            st.write(f"### Trang {i+1}")
            img_np = np.array(page)
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

<<<<<<< HEAD
            # Phát hiện ngôn ngữ tự động
=======
<<<<<<< HEAD
            # Phát hiện ngôn ngữ tự động
=======
>>>>>>> 2ba32ab (update requirement.txt)
>>>>>>> d426f62 (Initial commit on master)
            sample_text = pytesseract.image_to_string(img_bgr, config=custom_config, lang="vie+eng")
            try:
                lang_detected = detect(sample_text)
                lang = "vie" if lang_detected == "vi" else "eng"
            except:
                lang = "vie+eng"

            result_img, result_text = ocr_process(img_bgr, lang)
            st.image(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB), caption=f"OCR Trang {i+1}", use_container_width=True)
            st.text_area(f"📘 Văn bản Trang {i+1}", result_text, height=200)

    else:
        image = Image.open(uploaded_file)
        img_np = np.array(image)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

<<<<<<< HEAD
        # Phát hiện ngôn ngữ
=======
<<<<<<< HEAD
        # Phát hiện ngôn ngữ
=======
>>>>>>> 2ba32ab (update requirement.txt)
>>>>>>> d426f62 (Initial commit on master)
        sample_text = pytesseract.image_to_string(img_bgr, config=custom_config, lang="vie+eng")
        try:
            lang_detected = detect(sample_text)
            lang = "vie" if lang_detected == "vi" else "eng"
        except:
            lang = "vie+eng"

        result_img, result_text = ocr_process(img_bgr, lang)
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> d426f62 (Initial commit on master)

        st.image(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB), caption="Ảnh OCR", use_container_width=True)
        st.text_area("📘 Văn bản nhận dạng được", result_text, height=250)

<<<<<<< HEAD
=======
=======
        st.image(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB), caption="Ảnh OCR", use_container_width=True)
        st.text_area("📘 Văn bản nhận dạng được", result_text, height=250)
>>>>>>> 2ba32ab (update requirement.txt)
>>>>>>> d426f62 (Initial commit on master)
        st.download_button("📥 Tải kết quả OCR (.txt)",
                           data=result_text,
                           file_name="ocr_output.txt",
                           mime="text/plain")
<<<<<<< HEAD

else:
    st.info("⬆️ Tải lên ảnh hoặc PDF để bắt đầu nhận dạng.")
=======
<<<<<<< HEAD

else:
    st.info("⬆️ Tải lên ảnh hoặc PDF để bắt đầu nhận dạng.")
=======
else:
    st.info("⬆️ Tải lên ảnh hoặc PDF để bắt đầu nhận dạng.")
>>>>>>> 2ba32ab (update requirement.txt)
>>>>>>> d426f62 (Initial commit on master)
