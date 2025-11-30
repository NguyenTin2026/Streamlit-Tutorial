# ---------- Dockerfile ----------

# 1️⃣ Chọn base image Python nhẹ và mới nhất
FROM python:3.11-slim

# 2️⃣ Thiết lập thư mục làm việc
WORKDIR /app

# 3️⃣ Copy file requirements (chúng ta sẽ tạo file requirements.txt)
COPY requirements.txt .

# 4️⃣ Cài đặt dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ Copy toàn bộ project vào container
COPY . .

# 6️⃣ Expose cổng Streamlit mặc định
EXPOSE 8501

# 7️⃣ Lệnh chạy Streamlit khi container khởi động
CMD ["streamlit", "run", "Project-Forecast-Stocks-Exchange-Rate.py", "--server.port=8501", "--server.address=0.0.0.0"]

