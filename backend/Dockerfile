# STAGE 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Cài đặt các công cụ build cơ bản nếu cần biên dịch thư viện
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ ./requirements/

# Tạo virtual environment và cài đặt thư viện để tối ưu dung lượng
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /app/venv/bin/pip install --no-cache-dir -r requirements/base.txt

# STAGE 2: Runtime
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy virtual environment từ Stage 1
COPY --from=builder /app/venv /app/venv

# Copy source code của ứng dụng
COPY app/ ./app/

# Khởi tạo user không có đặc quyền root để chạy container an toàn
RUN useradd -u 8888 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port mặc định của ứng dụng
EXPOSE 8080

# Chạy Uvicorn Server gọi tới app.main:app
CMD ["/app/venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
