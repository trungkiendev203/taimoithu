# Tải Mọi Thứ - Backend (Phase 5)

Mã nguồn Backend cho dự án Tải Mọi Thứ. Sử dụng FastAPI, Redis và Celery.

## Cài đặt Môi trường & Chạy bằng Docker (Khuyên dùng)

Dự án đã được cấu hình đầy đủ bằng Docker Compose bao gồm API, Celery Worker và Redis:

```bash
# Khởi chạy toàn bộ hệ thống
docker-compose up --build
```

- API docs: `http://localhost:8000/docs`
- Health check nâng cao: `http://localhost:8000/api/v1/health`

## Chạy Local (Không Docker)

1. **Cài đặt thư viện:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Sao chép và cấu hình file `.env`:**
   ```bash
   cp .env.example .env
   ```
3. **Chạy Redis (Cần thiết cho Rate limiting, Celery & Job States).**
4. **Khởi chạy API Server:**
   ```bash
   uvicorn app.main:app --reload
   ```
5. **Khởi chạy Celery Worker:**
   ```bash
   celery -A app.core.celery_app worker --loglevel=info --concurrency=2
   ```

## Các tính năng Production Hardening (Phase 5)

Dự án không lưu trữ database hoặc file vĩnh viễn trên server mà áp dụng các cơ chế tự động hóa và giới hạn tài nguyên:

1. **Giới hạn tài nguyên (Free vs Premium):**
   - **Free (Mặc định)**: Dung lượng tải tối đa 50MB, tối đa 10 req/phút, tối đa 1 tiến trình tải đồng thời/IP.
   - **Premium**: Dung lượng tải tối đa 1GB, tối đa 30 req/phút, tối đa 3 tiến trình tải đồng thời/IP.
2. **License Key**:
   - Gửi key qua header `X-License-Key`.
   - Key mẫu mặc định: `TAIMOITHU_PREMIUM_KEY_2026`.
3. **Tự động xóa file tạm**:
   - File tạm trong `downloads/{job_id}/` được xóa ngay qua `BackgroundTasks` của FastAPI sau khi trình duyệt bắt đầu tải xong.
   - Một vòng lặp nền dọn dẹp thư mục downloads chạy mỗi 10 phút sẽ xóa toàn bộ các folder rác/stale folder có tuổi thọ lớn hơn 15 phút.
4. **Monitoring & Stats**:
   - `GET /api/v1/monitor/stats`: Thống kê số lượng phân tích và lượt tải ẩn danh theo tổng số và top IP.
   - `GET /api/v1/health`: Kiểm tra sức khỏe toàn diện (Redis, Celery Worker, dung lượng ổ đĩa).

## Chạy Kiểm thử (Tests)

```bash
docker-compose exec api python -m pytest
```

