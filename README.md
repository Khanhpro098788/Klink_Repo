# ⬡ KLINK AI - NỀN TẢNG SINH VIDEO AI & MẠNG XÃ HỘI (FULLSTACK CORE)

[![GCP](https://img.shields.io/badge/GCP-CloudRun%20%7C%20ArtifactRegistry-blue?logo=google-cloud&style=flat-square)](https://cloud.google.com/)
[![Docker](https://img.shields.io/badge/Docker-Multi--stage%20Build-blue?logo=docker&style=flat-square)](https://www.docker.com/)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions%20%7C%20WIF-green?logo=github-actions&style=flat-square)](https://github.com/features/actions)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python-green?logo=fastapi&style=flat-square)](https://fastapi.tailwindcss.com/)
[![Vite](https://img.shields.io/badge/Frontend-React%20%7C%20Vite%20%7C%20Redux-purple?logo=vite&style=flat-square)](https://vitejs.dev/)
[![C++](https://img.shields.io/badge/Core-C%2B%2B17%20%7C%20CUDA-orange?logo=c%2B%2B&style=flat-square)](https://isocpp.org/)

**Klink AI** là nền tảng sinh video AI tự động kết hợp mạng xã hội quy mô lớn. Dự án được thiết kế theo mô hình phân tách hoàn toàn **Frontend** (Web Client & Mobile App) và **Backend** (Python FastAPI Gateway, gRPC C++ Core Engine, Temporal.io Orchestrator), được đóng gói và vận hành tự động trên đám mây Google Cloud.

---

## 🧠 Sơ Đồ Kiến Trúc Hệ Thống & Luồng Dữ Liệu

Kiến trúc tương tác giữa các phân hệ được thiết kế tối ưu hóa tốc độ xử lý video 4K bằng phần cứng chuyên biệt (GPU NVIDIA) và cách ly lỗi:

```mermaid
sequenceDiagram
    autonumber
    actor User as Người dùng (React Web / Mobile App)
    participant API as FastAPI Gateway (Python)
    participant Redis as Redis (Pub/Sub)
    participant DB as MongoDB Atlas
    participant Temp as Temporal.io (Orchestrator)
    participant Qdrant as Qdrant Vector DB
    participant LLM as LLM Agent (Director)
    participant gRPC as gRPC Client (Python)
    participant CPP as gRPC C++ Server (Engine)
    participant GPU as NVIDIA NVENC/NVDEC
    participant GCS as Google Cloud Storage (GCS)

    %% Luồng Tư vấn Kịch bản RAG
    User->>API: POST /director/suggest-style (script_id)
    API->>Qdrant: Hybrid Search (Sparse/Dense) & Metadata Filter
    Qdrant-->>API: Trả về Top 5 Cinema Rules (Context)
    API->>LLM: Gọi LLM (Context + Script) & Re-ranking
    LLM-->>API: Trả về Technical JSON (Hiệu ứng, Nhịp điệu)
    API-->>User: Hiển thị gợi ý trên Timeline Editor

    %% Luồng Kích hoạt Render Video
    User->>API: POST /videos/render (script_id)
    API->>DB: Kiểm tra & Trừ Credit tạm tính (ACID Transaction)
    DB-->>API: Xác nhận thành công
    API->>Temp: Kích hoạt VideoRenderWorkflow (Saga Pattern)
    API-->>User: Trả về 202 Accepted (task_id)

    %% Luồng Temporal Workflow
    Note over Temp: Bắt đầu Workflow (State Persistence)
    Temp->>Temp: Activity 1: Download Assets (Cloudinary)
    Temp->>gRPC: Activity 2: Trigger Render (gRPC URL only)
    gRPC->>CPP: RPC Render(RenderRequest)
    
    %% Luồng C++ Engine
    Note over CPP: Khởi tạo CUDA Context
    CPP->>GPU: Hardware Decode (NVDEC) sang OpenCV Mat
    CPP->>CPP: Chỉ Crop vùng Bounding Box mặt (Tối ưu VRAM)
    CPP->>CPP: Face Blend & Overlay mặt AI nhép môi lên nền 4K
    CPP->>GPU: Hardware Encode (NVENC) sang MP4
    
    %% Báo cáo tiến độ Real-time
    loop Tiến trình xử lý video
        CPP->>Redis: PUBLISH task_{id}_progress (X%)
        Redis->>API: Nhận Event Progress
        API->>User: Đẩy qua WebSockets (Real-time Progress)
    end

    CPP-->>gRPC: Trả về RenderResponse (Success)
    gRPC-->>Temp: Báo cáo Activity 2 hoàn thành
    
    Temp->>Temp: Activity 3: Upload Output Video to GCS
    Temp->>DB: Activity 4: Cập nhật video_tasks (completed) & Thực thu Credit
    Note over Temp: Kết thúc Workflow thành công

    %% Trình duyệt nhận kết quả
    API-->>User: WebSockets gửi Event completed (result_url qua Cloudflare CDN)
```

### Các Kỹ Thuật Tối Ưu Hiệu Năng Cốt Lõi:
1. **Pass-by-Reference (Truyền tham chiếu):** Không truyền mảng byte video thô qua mạng gRPC hay Temporal. Tất cả giao tiếp chỉ truyền URL hoặc đường dẫn file cục bộ.
2. **Bounding Box Face Crop:** Nhép môi AI (`Wav2Lip`) chỉ xử lý trên ô vuông khuôn mặt nhỏ (ví dụ 256x256), sau đó C++ dùng OpenCV blend trở lại nền 4K gốc. Tiết kiệm 90% tải GPU và giữ nguyên độ nét 4K của video.
3. **NVIDIA Hardware Acceleration:** Đẩy toàn bộ tác vụ decode/encode video sang chip chuyên dụng **NVENC/NVDEC** trên GPU, giải phóng 100% tài nguyên CPU.
4. **Saga Pattern (Temporal.io):** Quản lý luồng công việc dài hạn. Nếu node C++ bị crash giữa chừng, Temporal sẽ ghi nhớ trạng thái và tự động retry đúng bước lỗi thay vì chạy lại từ đầu.

---

## 🚀 Hạ Tầng Google Cloud & Quy Trình CI/CD (DevOps)

Hệ thống được thiết kế theo tiêu chuẩn DevOps tự động hóa hoàn toàn từ mã nguồn đến triển khai, đảm bảo tính sẵn sàng vận hành và bảo mật cao.

### 1. Kiến trúc Đám mây (GCP Architecture)
*   **Google Cloud Run**: 
    *   `fastapi-demo-project` (Backend): Chạy ứng dụng API Gateway Python FastAPI.
    *   `frontend-service` (Frontend): Chạy ứng dụng React + Vite thông qua web server Nginx siêu nhẹ.
*   **Google Artifact Registry**: Kho lưu trữ tập trung Docker Images tối ưu cho Backend và Frontend.
*   **VPC & Tường lửa nội bộ**: Hệ thống mạng VPC độc lập (`day13-vpc`) thiết lập chặn Egress mặc định (`deny-all-egress`) và chỉ mở luồng kết nối tới API Google an toàn để tránh rò rỉ dữ liệu.
*   **Identity & Access Management (IAM)**: 
    *   Áp dụng nguyên lý **Đặc quyền tối thiểu (Least Privilege)**. Tách biệt Robot build/deploy (`github-ci-sa`) và Robot chạy thực tế lúc runtime (`cloudrun-runtime-sa`).

### 2. Pipeline Tự động hóa CI/CD (GitHub Actions)
Pipeline được khai báo trong `.github/workflows/ci.yml` tự động kích hoạt khi có sự kiện `push` lên nhánh `main` hoặc `deploy`:

```text
[Code Push] ──> [1. Chạy Test Pytest & Mock MongoDB] ──> [2. Xác thực GCP bằng WIF (OIDC)]
                       │
                       └──> [3. Build & Push Docker Images (Backend & Frontend)]
                                   │
                                   └──> [4. Lấy URL API động & Inject vào Frontend]
                                               │
                                               └──> [5. Triển khai lên Google Cloud Run]
```

*   **Bộ nhớ đệm (Caching)**: Tối ưu hóa hiệu năng bằng cách lưu cache thư viện python (`pip`) và cache các layer của Docker Buildx (`gha`).
*   **Bảo mật WIF (Workload Identity Federation)**: Kết nối giữa GitHub và Google Cloud thông qua mã thông báo OIDC động tồn tại trong 1 giờ, loại bỏ hoàn toàn việc lưu khóa JSON tĩnh nguy hiểm.

### 3. Giám sát & Cảnh báo (Observability)
*   **Structured JSON Logging**: Log của API được định dạng cấu trúc JSON, tự động bọc Trace ID (`X-Cloud-Trace-Context`) để dễ dàng truy vết sự cố trên **Logs Explorer**.
*   **Cảnh báo Alerting (Email)**:
    *   **5xx Error Alert**: Báo động ngay lập tức nếu phát hiện bất kỳ lỗi hệ thống HTTP 5xx nào trong vòng 1 phút, đính kèm link Sổ tay cứu hộ (`docs/runbooks/alert_5xx.md`).
    *   **Latency Alert**: Báo động nếu độ trễ phân vị p95 vượt quá 2 giây liên tục trong 5 phút.
*   **Performance Dashboard**: Bảng điều khiển giám sát trực quan 2 thông số vàng: **Traffic (Request Count)** và **Latency (Độ trễ p95)**.

---

## 🌳 Cấu Trúc Thư Mục Dự Án (Domain-Driven Design)

```text
klink-platform/
├── .env                          # Biến môi trường local (đã cấu hình GCP & AWS)
├── .env.example                  # File cấu hình mẫu cho nhà phát triển
├── docker-compose.yml            # Khởi chạy MongoDB, Redis, Qdrant, Temporal
├── sst.config.ts                 # Cấu hình IaC (SST v3) khai báo hạ tầng Cloud Run & Alerting
│
├── backend/                      # ==========================================
│   │                             # PHÂN HỆ BACKEND (Python FastAPI & C++)
│   │                             # ==========================================
│   ├── cpp_engine/               # LÕI XỬ LÝ VIDEO BẰNG C++ (Core Engine GPU)
│   │   ├── CMakeLists.txt        # Cấu hình biên dịch C++ (CUDA, OpenCV, gRPC)
│   │   ├── proto/                # Định nghĩa cấu trúc gRPC Protobuf
│   │   └── app/                  # Source code C++ (.cpp)
│   │
│   ├── app/                      # HỆ THỐNG WEB API & ORCHESTRATOR (Python FastAPI)
│   │   ├── main.py               # API Gateway & Structured Logging Middleware
│   │   ├── config.py             # Cấu hình Global BaseSettings của ứng dụng
│   │   ├── auth/                 # Phân hệ Xác thực & Tài khoản (JWT, bcrypt)
│   │   ├── rag/                  # Phân hệ AI RAG Director (LangChain, Qdrant)
│   │   ├── temporal_worker/      # ĐIỀU PHỐI WORKFLOW (Temporal Worker)
│   │   └── grpc_clients/         # Client giao tiếp với cpp_engine qua gRPC
│   │
│   ├── tests/                    # Bộ kiểm thử tự động (Pytest)
│   └── requirements/             # Khai báo các thư viện Python (base.txt & dev.txt)
│
├── frontend-web/                 # ==========================================
│   │                             # PHÂN HỆ FRONTEND WEB (ReactJS + Vite)
│   │                             # ==========================================
│   ├── Dockerfile                # Đóng gói 2 giai đoạn (Multi-stage Node & Nginx)
│   ├── vite.config.js            # Cấu hình build system Vite
│   └── app/
│       ├── main.jsx              # Điểm khởi chạy React app
│       ├── App.jsx               # Cấu hình routing và layouts chính
│       ├── services/api.js       # Axios client nhận API URL động (VITE_API_URL)
│       └── store/                # Quản lý State toàn cục bằng Redux Toolkit
│
└── docs/                         # ==========================================
    ├── runbooks/                 # Sổ tay hướng dẫn xử lý sự cố (alert_5xx.md)
    ├── postmortems/              # Báo cáo phân tích sự cố (incident_5xx_crash.md)
    └── production_readiness.md   # Bảng checklist đánh giá sẵn sàng vận hành (PRR)
```

---

## 🛠️ Hướng Dẫn Cài Đặt Môi Trường (Local Setup)

### 1. Cài đặt C++ Engine Dependencies (NVIDIA SDK, OpenCV, gRPC)
*   **CUDA Toolkit:** Cài đặt CUDA Toolkit bản 12.x trở lên. Kiểm tra bằng lệnh `nvcc --version`.
*   **NVIDIA Video Codec SDK (NVENC/NVDEC):** Tải và cấu hình SDK từ trang chủ NVIDIA Developer.
*   **OpenCV CUDA Support:** Biên dịch OpenCV từ source code với flag `WITH_CUDA=ON`, `WITH_CUDNN=ON`.
*   **gRPC C++:** Cài đặt gRPC & Protobuf từ source code bằng CMake.

### 2. Cài đặt Python Backend Dependencies
Yêu cầu Python 3.11+. Khởi chạy môi trường ảo:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Hoặc .venv\Scripts\activate trên Windows
pip install -r requirements/base.txt -r requirements/dev.txt
```

### 3. Cài đặt Frontend Web Dependencies
Yêu cầu cài đặt **Node.js (v18+)** và **npm**:
```bash
cd frontend-web
npm install
```

---

## 🚀 Hướng Dẫn Chạy Dự Án (Startup Guide)

Khởi chạy toàn bộ hệ thống ở môi trường local theo thứ tự các bước sau:

### Bước 1: Khởi động các Service Hạ tầng (Docker)
```bash
docker-compose up -d mongodb redis qdrant temporal
```

### Bước 2: Setup Database & Tạo Indexes MongoDB
```bash
cd backend
python scripts/setup_indexes.py
```

### Bước 3: Biên dịch và Chạy gRPC C++ Engine Server (Port 50051)
```bash
cd backend/cpp_engine
mkdir build && cd build
cmake ..
make -j$(nproc)
./klink_cpp_engine
```

### Bước 4: Khởi chạy Temporal Worker (Python)
```bash
cd backend
python -m app.temporal_worker.worker
```

### Bước 5: Khởi chạy FastAPI Web API Gateway
```bash
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Swagger UI sẽ khả dụng tại: `http://127.0.0.1:8000/docs`

### Bước 6: Khởi chạy Frontend Web (ReactJS / Vite)
```bash
cd frontend-web
npm run dev
```
Trình duyệt sẽ mở ứng dụng tại: `http://localhost:5173`

---

## 🏆 Tiêu Chuẩn Hoàn Thành (Definition of Done - DoD)
*   **Frontend-Web:** Timeline editor lưu trữ trạng thái scene hoàn toàn đồng bộ thông qua Redux Toolkit, tự động hiển thị thanh tiến trình render thông qua kết nối WebSocket với backend.
*   **C++ Engine:** Xử lý video 4K không rò rỉ bộ nhớ (Memory Leak), giải phóng CUDA Context đúng cách sau mỗi request.
*   **Temporal Saga:** Tự phục hồi trạng thái thành công khi node gRPC C++ Server đột ngột tắt và hồi phục lại.
*   **MongoDB:** Mọi giao dịch ví credit bắt buộc phải bọc trong MongoDB ACID Session (`start_transaction`) để đảm bảo tính nhất quán dữ liệu.