# =========================================================
# Project 3 Ultimate: Professional Media Analysis & Object Detection Dashboard
import streamlit as st
from PIL import Image
import numpy as np
import cv2
import tempfile
from ultralytics import YOLO
import pandas as pd
import plotly.express as px

# =========================================================
# Page config
st.set_page_config(page_title='Ultimate Media Dashboard', layout='wide', page_icon='🤖')
st.title('📌 Ultimate Media & Object Detection Dashboard')

# =========================================================
# Dark / Light theme toggle (simple)
theme = st.radio('🌗 Theme', ['Light', 'Dark'])
if theme == 'Dark':
    st.markdown(
        "<style>body{background-color:#0b0e1a;color:white;} </style>", unsafe_allow_html=True
    )

# =========================================================
# Load YOLOv8 model (cache)
@st.cache_resource
def load_model():
    model = YOLO('yolov8n.pt')  # small, fast
    return model

model = load_model()

# =========================================================
# Multi-file upload
uploaded_files = st.file_uploader('Upload Images / Videos', type=['png','jpg','jpeg','mp4','avi'], accept_multiple_files=True)
if uploaded_files:
    results_summary = []
    for uploaded_file in uploaded_files:
        file_type = uploaded_file.type
        st.subheader(f'📂 File: {uploaded_file.name}')

        # =========================================================
        # IMAGE
        if 'image' in file_type:
            img = Image.open(uploaded_file)
            st.image(img, caption='Original Image', use_column_width=True)

            img_array = np.array(img)
            results = model(img_array)[0]
            annotated_img = results.plot()
            st.image(annotated_img, caption='Detected Objects', use_column_width=True)

            # Count objects per class
            classes = results.names
            counts = {}
            for cls in results.boxes.cls:
                cls_name = classes[int(cls)]
                counts[cls_name] = counts.get(cls_name, 0) + 1
            results_summary.append({'file': uploaded_file.name, **counts})

            # Download processed image
            processed_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            Image.fromarray(annotated_img).save(processed_file.name)
            st.download_button('📥 Download Processed Image', data=open(processed_file.name,'rb'), file_name=f'detected_{uploaded_file.name}')

        # =========================================================
        # VIDEO
        elif 'video' in file_type:
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(uploaded_file.read())
            st.video(tfile.name)

            cap = cv2.VideoCapture(tfile.name)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            st.text(f'Processing video {uploaded_file.name} ({frame_count} frames)...')

            out_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(out_file.name, fourcc, fps, (width, height))

            video_counts = {}

            for i in range(frame_count):
                ret, frame = cap.read()
                if not ret:
                    break
                results = model(frame)[0]
                annotated_frame = results.plot()
                out.write(cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR))
                # Count objects per class in this frame
                for cls in results.boxes.cls:
                    cls_name = results.names[int(cls)]
                    video_counts[cls_name] = video_counts.get(cls_name,0)+1

            cap.release()
            out.release()

            st.video(out_file.name)
            st.download_button('📥 Download Processed Video', data=open(out_file.name,'rb'), file_name=f'detected_{uploaded_file.name}')
            results_summary.append({'file': uploaded_file.name, **video_counts})

    # =========================================================
    # Summary Table & Charts
    if results_summary:
        st.subheader('📊 Detection Summary')
        df_summary = pd.DataFrame(results_summary).fillna(0)
        st.dataframe(df_summary)

        # Chart: objects per file
        st.subheader('📈 Object Counts per File')
        object_cols = df_summary.columns.drop('file')
        df_melt = df_summary.melt(id_vars='file', value_vars=object_cols, var_name='Class', value_name='Count')
        fig = px.bar(df_melt, x='file', y='Count', color='Class', title='Objects detected per file', barmode='stack')
        st.plotly_chart(fig, use_container_width=True)

        # Download CSV summary
        csv_bytes = df_summary.to_csv(index=False).encode('utf-8')
        st.download_button('📥 Download Detection Summary CSV', data=csv_bytes, file_name='detection_summary.csv', mime='text/csv')

st.success('🎯 Ultimate Media Analysis Project Completed – Professional & Portfolio-ready!')
