import time
import logging
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.database import db_manager
from app.auth.router import router as auth_router

# Thiết lập Google Cloud Logging với phương án dự phòng (fallback) khi chạy local
try:
    import google.cloud.logging
    client = google.cloud.logging.Client()
    client.setup_logging()
except Exception:
    logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect database
    db_manager.connect()
    yield
    # Disconnect database
    db_manager.disconnect()

app = FastAPI(
    title="Klink AI Video Core Platform",
    description="Fullstack Polyglot AI Video Platform Backend",
    version="1.0.0",
    lifespan=lifespan
)

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware tự động bắt Trace ID và định dạng Log chuẩn JSON
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Trích xuất Trace ID từ Google Cloud Ingress Header
    trace_header = request.headers.get("X-Cloud-Trace-Context", "unknown-trace")
    trace_id = trace_header.split("/")[0] if "/" in trace_header else trace_header

    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    status_code = response.status_code
    
    # Xác định mức độ nghiêm trọng (Severity) dựa trên HTTP Status Code
    severity = "INFO"
    if status_code >= 400:
        severity = "WARNING"
    if status_code >= 500:
        severity = "ERROR"
    
    log_data = {
        "message": f"{request.method} {request.url.path} finished in {process_time:.2f}ms",
        "method": request.method,
        "path": request.url.path,
        "status_code": status_code,
        "process_time_ms": process_time,
        "trace": trace_id,
        "severity": severity
    }
    
    # Ghi log dạng cấu trúc JSON
    if severity == "ERROR":
        logging.error(json.dumps(log_data))
    elif severity == "WARNING":
        logging.warning(json.dumps(log_data))
    else:
        logging.info(json.dumps(log_data))
        
    return response

# Register routers
app.include_router(auth_router)

@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "healthy", "service": "klink-api-gateway"}

@app.get("/crash", tags=["system"])
async def trigger_crash():
    # Chỉ cho phép kích hoạt lỗi ở môi trường dev/local để tránh bị lạm dụng ở production
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=403,
            detail="Crash simulation is not allowed in production environment"
        )
    # Giả lập lỗi 500 phục vụ test Alerting
    raise HTTPException(status_code=500, detail="Intentional system crash for alerting test")
