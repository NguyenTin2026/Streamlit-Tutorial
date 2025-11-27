import streamlit as st
import torch
import torchxrayvision as xrv
from PIL import Image
import numpy as np
import plotly.express as px
import pandas as pd

# Cấu hình trang Streamlit
st.set_page_config(page_title="X-Ray Disease Detection Created By Mr. TinTinDo", layout="wide")
st.title("X-Ray Disease Detection (Màu sắc theo xác suất: Đỏ → Vàng → Xanh lá)")

# Giải thích các loại bệnh (tiếng Việt)
disease_info = {
    "Atelectasis": "Xẹp phổi một phần hoặc toàn bộ.",  # Collapse of part or all of a lung
    "Cardiomegaly": "Tim to bất thường.",  # Enlarged heart
    "Effusion": "Dịch tích tụ quanh phổi.",  # Fluid accumulation around the lungs
    "Infiltration": "Sự xuất hiện chất lạ trong phổi.",  # Presence of foreign material in lungs
    "Mass": "Khối u hoặc bướu trong phổi.",  # A lump or mass in the lung
    "Nodule": "Đốm mờ nhỏ trong phổi.",  # Small rounded opacity in lungs
    "Pneumonia": "Viêm phổi.",  # Infection causing lung inflammation
    "Pneumothorax": "Khí trong khoang màng phổi gây xẹp phổi.",  # Air in the pleural space causing lung collapse
    "Consolidation": "Mô phổi chứa đầy dịch thay vì khí.",  # Lung tissue filled with liquid instead of air
    "Edema": "Dịch tích tụ trong phổi.",  # Fluid accumulation in lungs
    "Emphysema": "Tổn thương phế nang gây khó thở.",  # Damage to alveoli causing shortness of breath
    "Fibrosis": "Mô phổi dày lên và sẹo hóa.",  # Thickening and scarring of lung tissue
    "Pleural_Thickening": "Lớp màng quanh phổi dày lên.",  # Thickening of the lining around lungs
    "Hernia": "Nội tạng lồi ra ngoài qua thành cơ thể."  # Protrusion of organ through a cavity wall
}

# Hàm load mô hình DenseNet đã được train sẵn
@st.cache_resource
def load_model():
    model = xrv.models.DenseNet(weights="densenet121-res224-all")  # Load DenseNet121 pretrained
    model.eval()  # Chuyển sang chế độ evaluation
    return model

model = load_model()  # Load mô hình

# Upload ảnh X-ray
uploaded_file = st.file_uploader("Upload X-Ray Image", type=["png","jpg","jpeg"])
if uploaded_file:
    # Chuyển ảnh sang grayscale (1 kênh)
    img = Image.open(uploaded_file).convert('L')
    st.image(img, caption='Ảnh X-Ray đã upload', use_column_width=True)
    
    # Resize ảnh về 224x224 để phù hợp với input DenseNet
    img = img.resize((224,224))
    
    # Chuyển từ PIL Image -> Tensor [1,1,224,224], chuẩn hóa giá trị 0-1
    input_tensor = torch.from_numpy(np.array(img)).unsqueeze(0).unsqueeze(0).float() / 255.0
    
    # Dự đoán xác suất các bệnh
    with torch.no_grad():
        output = torch.sigmoid(model(input_tensor))  # Sigmoid để nhận xác suất từ 0-1
    
    labels = model.pathologies  # Danh sách 14 bệnh
    predictions = {label: float(prob) for label, prob in zip(labels, output[0])}  # Map bệnh -> xác suất
    
    # Sắp xếp các bệnh theo xác suất giảm dần
    sorted_preds = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
    
    # Hiển thị kết quả với màu theo xác suất: Top 1 đỏ, Top 2-3 vàng, còn lại xanh lá
    st.subheader("Dự đoán (Top 1: Đỏ, Top 2–3: Vàng, Còn lại: Xanh lá):")
    for i, (disease, prob) in enumerate(sorted_preds):
        if i == 0:
            st.markdown(f"**:red[{disease}: {prob:.3f}]**")      # Top 1 đỏ
        elif i <= 2:
            st.markdown(f"**:yellow[{disease}: {prob:.3f}]**")   # Top 2-3 vàng
        else:
            st.markdown(f"**:green[{disease}: {prob:.3f}]**")    # Còn lại xanh lá
    
    # Chuẩn bị DataFrame cho biểu đồ Plotly
    colors = []
    for i in range(len(sorted_preds)):
        if i == 0:
            colors.append("red")
        elif i <= 2:
            colors.append("yellow")
        else:
            colors.append("green")
    
    df = pd.DataFrame({
        "Disease": [d for d,_ in sorted_preds],  # Tên bệnh
        "Probability": [p for _,p in sorted_preds],  # Xác suất
        "Info": [disease_info.get(d, "Không có mô tả") for d,_ in sorted_preds],  # Mô tả tiếng Việt
        "Color": colors  # Màu tương ứng
    })
    
    # Biểu đồ cột tương tác với Plotly
    st.subheader("Biểu đồ dự đoán tương tác:")
    fig = px.bar(df, x="Disease", y="Probability", color="Color", 
                 color_discrete_map={"red":"red", "yellow":"yellow", "green":"green"},
                 hover_data={"Disease": True, "Probability": ':.3f', "Info": True, "Color": False})
    fig.update_layout(xaxis_tickangle=-45, yaxis_range=[0,1])  # Xoay tên bệnh, giới hạn trục Y
    st.plotly_chart(fig, use_container_width=True)  # Hiển thị biểu đồ trên Streamlit
