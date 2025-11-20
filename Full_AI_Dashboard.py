# =========================================================
# Project 5: Full AI Dashboard – Images, Video & Webcam
import streamlit as st
from PIL import Image
import numpy as np
import cv2
import tempfile
import pandas as pd
import plotly.express as px
from ultralytics import YOLO

# =========================================================
# Page config
st.set_page_config(page_title='Ultimate AI Dashboard', layout='wide', page_icon='🤖')
st.title('📌 Ultimate AI Dashboard – Images, Video & Webcam Detection')

# =========================================================
# Theme toggle
theme = st.radio('🌗 Theme', ['Light', 'Dark'])
if theme == 'Dark':
    st.markdown("<style>body{background-color:#0b0e1a;color:white;} </style>", unsafe_allow_html=True)

# =========================================================
# Load YOLOv8 model (cache)
@st.cache_resource
def load_model():
    return YOLO('yolov8n.pt')

model = load_model()

# =========================================================
# Sidebar: multi-tab UI
tab = st.sidebar.radio('Chọn tab', ['📁 Upload Media', '🎥 Webcam Detection', '📊 Analytics'])

# =========================================================
# GLOBAL STORAGE
if 'results_summary' not in st.session_state:
    st.session_state.results_summary = []

# =========================================================
# TAB 1: Multi-file Upload
if tab == '📁 Upload Media':
    st.header('Upload Images / Videos')
    uploaded_files = st.file_uploader('Chọn file', type=['png','jpg','jpeg','mp4','avi'], accept_multiple_files=True)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.subheader(f'File: {uploaded_file.name}')
            file_type = uploaded_file.type

            # Image
            if 'image' in file_type:
                img = Image.open(uploaded_file)
                st.image(img, caption='Original Image', use_column_width=True)
                img_array = np.array(img)
                results = model(img_array)[0]
                annotated_img = results.plot()
                st.image(annotated_img, caption='Detected Objects', use_column_width=True)

                # Count objects per class
                counts = {}
                for cls in results.boxes.cls:
                    cls_name = results.names[int(cls)]
                    counts[cls_name] = counts.get(cls_name,0)+1
                st.session_state.results_summary.append({'file': uploaded_file.name, **counts})

                # Download processed image
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                Image.fromarray(annotated_img).save(temp_file.name)
                st.download_button('📥 Download Processed Image', data=open(temp_file.name,'rb'), file_name=f'detected_{uploaded_file.name}')

            # Video
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
                out = cv2.VideoWriter(out_file.name, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
                video_counts = {}

                for i in range(frame_count):
                    ret, frame = cap.read()
                    if not ret:
                        break
                    results = model(frame)[0]
                    annotated_frame = results.plot()
                    out.write(cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR))
                    for cls in results.boxes.cls:
                        cls_name = results.names[int(cls)]
                        video_counts[cls_name] = video_counts.get(cls_name,0)+1

                cap.release()
                out.release()
                st.video(out_file.name)
                st.download_button('📥 Download Processed Video', data=open(out_file.name,'rb'), file_name=f'detected_{uploaded_file.name}')
                st.session_state.results_summary.append({'file': uploaded_file.name, **video_counts})

# =========================================================
# TAB 2: Real-time Webcam Detection
elif tab == '🎥 Webcam Detection':
    st.header('Real-time Webcam Detection')
    run_detection = st.checkbox('Start Detection', value=False)
    selected_classes = st.multiselect('Chọn class hiển thị (bỏ trống = all)', model.names.values(), default=[])

    if run_detection:
        cap = cv2.VideoCapture(0)
        frame_placeholder = st.empty()
        stop_button = st.button('Stop Detection')
        summary = {}

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or stop_button:
                break

            results = model(frame)[0]
            if selected_classes:
                mask = [model.names[int(cls)] in selected_classes for cls in results.boxes.cls]
                results.boxes = results.boxes[mask]

            annotated_frame = results.plot()
            for cls in results.boxes.cls:
                cls_name = model.names[int(cls)]
                summary[cls_name] = summary.get(cls_name,0)+1

            frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels='RGB', use_column_width=True)

        cap.release()
        st.success('🛑 Detection stopped')
        if summary:
            st.session_state.results_summary.append({'file':'Webcam', **summary})

# =========================================================
# TAB 3: Analytics & Summary
elif tab == '📊 Analytics':
    st.header('Detection Summary & Analytics')
    if st.session_state.results_summary:
        df_summary = pd.DataFrame(st.session_state.results_summary).fillna(0)
        st.dataframe(df_summary)

        # Interactive chart
        object_cols = df_summary.columns.drop('file')
        df_melt = df_summary.melt(id_vars='file', value_vars=object_cols, var_name='Class', value_name='Count')
        fig = px.bar(df_melt, x='file', y='Count', color='Class', title='Objects Detected per File', barmode='stack')
        st.plotly_chart(fig, use_container_width=True)

        # Download CSV
        csv_bytes = df_summary.to_csv(index=False).encode('utf-8')
        st.download_button('📥 Download Detection Summary CSV', data=csv_bytes, file_name='full_dashboard_summary.csv', mime='text/csv')
    else:
        st.info('No detection results yet. Upload media or run webcam detection.')

st.success('🎯 Ultimate AI Dashboard Ready – Portfolio-Professional!')
