# =========================================================
# Streamlit Ultimate Dashboard: CSV + To-Do List (auto detect sep & encoding)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import chardet  # để detect encoding

# =========================================================
# Page Config
st.set_page_config(
    page_title='Streamlit Ultimate Dashboard',
    layout='wide',
    page_icon='📊'
)

st.title('📌 Ultimate CSV Dashboard & To-Do List (Auto detect CSV)')

# =========================================================
# 1️⃣ To-Do List
st.header('📝 To-Do List')
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

new_task = st.text_input('Thêm nhiệm vụ mới:')
if st.button('Thêm nhiệm vụ'):
    if new_task.strip():
        st.session_state.tasks.append(new_task)
        st.success(f"✅ Đã thêm: {new_task}")
    else:
        st.warning('⚠️ Hãy nhập nhiệm vụ trước!')

st.subheader('Danh sách nhiệm vụ')
tasks_to_remove = []
for i, task in enumerate(st.session_state.tasks):
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.write(f"{i+1}. {task}")
    with col2:
        if st.button('❌ Xóa', key=f"del{i}"):
            tasks_to_remove.append(i)

for i in reversed(tasks_to_remove):
    st.session_state.tasks.pop(i)
if tasks_to_remove:
    st.rerun()

st.divider()

# =========================================================
# 2️⃣ CSV Dashboard với auto detect
st.header('📂 CSV Dashboard (Auto detect sep & encoding)')

uploaded_file = st.file_uploader('Upload CSV', type=['csv'])
if uploaded_file:
    # =========================================================
    # Detect encoding
    rawdata = uploaded_file.read()
    result = chardet.detect(rawdata)
    encoding = result['encoding']
    uploaded_file.seek(0)  # reset pointer

    # Detect separator (comma, semicolon, tab)
    sample = rawdata[:1000].decode(encoding)
    if sample.count(';') > sample.count(','):
        sep = ';'
    elif sample.count('\t') > sample.count(','):
        sep = '\t'
    else:
        sep = ','

    # Load CSV
    df = pd.read_csv(uploaded_file, sep=sep, encoding=encoding)
    st.success(f'✅ File đã tải lên | Encoding: {encoding}, Separator: "{sep}"')

    # Map 0/1 → Vật/Không vật
    for col in df.select_dtypes(include=[np.int64, np.int32]):
        if df[col].dropna().isin([0,1]).all():
            df[col] = df[col].map({0: 'Không vật', 1: 'Vật'})

    # =========================================================
    # Column selection
    st.subheader('🔹 Chọn cột hiển thị')
    cols = st.multiselect("Chọn cột", df.columns.tolist(), default=df.columns[:5])
    filtered_df = df.copy()

    # =========================================================
    # Filter & Search
    st.subheader('🔍 Filter & Search')
    for col in cols:
        if filtered_df[col].dtype == object:
            values = st.multiselect(f'Lọc {col}', options=filtered_df[col].unique(), default=filtered_df[col].unique())
            filtered_df = filtered_df[filtered_df[col].isin(values)]
        elif np.issubdtype(filtered_df[col].dtype, np.number):
            min_val, max_val = st.slider(
                f'Lọc {col}', float(filtered_df[col].min()), float(filtered_df[col].max()),
                (float(filtered_df[col].min()), float(filtered_df[col].max()))
            )
            filtered_df = filtered_df[(filtered_df[col] >= min_val) & (filtered_df[col] <= max_val)]

    # =========================================================
    # Pagination
    st.subheader('📄 Preview dữ liệu với Pagination')
    page_size = st.number_input('Số dòng mỗi trang', min_value=10, max_value=1000, value=100)
    total_pages = max(1, int(np.ceil(len(filtered_df) / page_size)))
    page = st.number_input('Trang hiện tại', min_value=1, max_value=total_pages, value=1)
    start = (page-1)*page_size
    end = start + page_size
    st.dataframe(filtered_df.iloc[start:end][cols])

    # =========================================================
    # Charts Realtime
    st.subheader('📊 Charts Realtime')
    numeric_cols = filtered_df.select_dtypes(include=np.number).columns.tolist()
    if len(numeric_cols) >= 2:
        x_col = st.selectbox('Chọn cột X (numeric)', numeric_cols, index=0)
        y_col = st.selectbox('Chọn cột Y (numeric)', numeric_cols, index=1)
        color_col = st.selectbox('Chọn cột color', [None]+cols, index=0)
        chart_type = st.selectbox('Chọn loại chart', ['Scatter', 'Bar', 'Line'])
        if chart_type == 'Scatter':
            fig = px.scatter(filtered_df, x=x_col, y=y_col, color=color_col, title=f'{x_col} vs {y_col}')
        elif chart_type == 'Bar':
            fig = px.bar(filtered_df, x=x_col, y=y_col, color=color_col, title=f'{x_col} vs {y_col}')
        else:
            fig = px.line(filtered_df, x=x_col, y=y_col, color=color_col, title=f'{x_col} vs {y_col}')
        st.plotly_chart(fig, use_container_width=True)

    # =========================================================
    # JSON Preview
    st.subheader('JSON Preview')
    st.json(filtered_df.head(100).to_dict(orient='records'))

    # =========================================================
    # Download CSV
    st.subheader('📥 Download CSV đã lọc')
    csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button('Tải CSV về', csv_bytes, file_name='Filtered_data.csv', mime='text/csv')

    st.success('🎯 Project hoàn chỉnh – tự detect CSV, xử lý mượt, không hallucination!')
