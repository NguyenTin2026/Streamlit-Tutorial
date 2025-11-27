import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import tempfile
import threading
import os

# --------- Streamlit config ---------
st.set_page_config(page_title="YOLOv8 Object Detection", layout="wide")
st.title("📸 Object Detection (YOLOv8)")

# --------- Load YOLOv8 model ---------
@st.cache_resource
def load_model(model_path="yolov8n.pt"):
    model = YOLO(model_path)
    return model

model = load_model()

# --------- Sidebar options ---------
st.sidebar.title("Options")
input_type = st.sidebar.radio("Select input type:", ["Image", "Video", "Webcam"])
confidence_threshold = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.25, 0.05)

# --------- Helper functions ---------
def get_detection_dataframe(results, model):
    return pd.DataFrame({
        "Class": [model.names[int(cls)] for cls in results.boxes.cls],
        "Confidence": [float(conf) for conf in results.boxes.conf]
    })

def display_image_results(img, results):
    annotated_img = results.plot()
    st.image(cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB))
    df = get_detection_dataframe(results, model)
    st.subheader("Detection Results")
    st.dataframe(df)
    if not df.empty:
        st.bar_chart(df.groupby("Class")["Confidence"].mean())

# --------- Image input ---------
if input_type == "Image":
    file = st.file_uploader("Upload Image", type=["jpg","jpeg","png"])
    if file:
        img = Image.open(file)
        st.image(img, caption="Uploaded Image", use_column_width=True)
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        results = model.predict(img_cv, conf=confidence_threshold)[0]
        display_image_results(img_cv, results)
        # Export result
        if st.button("Download Annotated Image"):
            result_img_path = "annotated_image.jpg"
            cv2.imwrite(result_img_path, results.plot())
            st.download_button("Download", data=open(result_img_path, "rb"), file_name="annotated_image.jpg")
            os.remove(result_img_path)

# --------- Video input ---------
elif input_type == "Video":
    file = st.file_uploader("Upload Video", type=["mp4","mov","avi"])
    if file:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(file.read())
        cap = cv2.VideoCapture(tfile.name)
        stframe = st.empty()

        # Multi-thread video processing
        def process_video():
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                results = model.predict(frame, conf=confidence_threshold)[0]
                frame = results.plot()
                stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            cap.release()

        threading.Thread(target=process_video).start()

# --------- Webcam input ---------
elif input_type == "Webcam":
    img_file = st.camera_input("Use Webcam")
    if img_file:
        img = Image.open(img_file)
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        results = model.predict(img_cv, conf=confidence_threshold)[0]
        display_image_results(img_cv, results)
