# Kế Hoạch Triển Khai Backend (Phase 3) - Download Pipeline

Phase 3 là phase phức tạp nhất của Backend, chuyển từ xử lý luồng đồng bộ sang bất đồng bộ hoàn toàn sử dụng Message Queue. Dưới đây là kế hoạch chi tiết.

## Proposed Changes (Các thay đổi dự kiến)

### 1. Cấu hình Redis & Celery
- **`backend/requirements.txt`**: Bổ sung `celery`, `redis`, `sse-starlette` (để hỗ trợ Server-Sent Events).
- **`backend/app/core/celery_app.py`**: Khởi tạo app Celery, định cấu hình kết nối tới Redis (sử dụng như Broker và Backend để lưu trữ status).
- **`backend/docker-compose.yml`**: Thêm service `redis` và service `worker` chạy lệnh `celery -A app.core.celery_app worker`.

### 2. Định nghĩa Schema & State
- **`backend/app/schemas/download.py`**: Tạo các model `DownloadRequest`, `BatchDownloadRequest`.
- **`backend/app/schemas/job.py`**: Model quản lý trạng thái Job (Job ID, Status: PENDING, PROCESSING, COMPLETED, FAILED), Progress (%).
- Xây dựng class Singleton/Redis helper để lưu trữ state của Job trực tiếp trên Redis thay vì Postgres (Phase này chỉ thiết lập Redis để nhẹ nhàng và đáp ứng ngay E2E flow).

### 3. Worker Tasks (Logic Tải File)
- **`backend/app/worker/tasks.py`**:
  - Task `download_video_task(job_id, url, format_id)`:
    - Tạo thư mục tạm `/tmp/taimoithu/<job_id>`.
    - Dùng `yt-dlp` download với progress hook.
    - Trong progress hook, emit sự kiện (Pub/Sub) lên Redis để API SSE bắt được.
    - Dùng FFmpeg (nếu cần merge audio/video).
    - Tạo link tải trực tiếp (hoặc giả lập trong Phase 3 trước khi cắm S3 thật ở Phase 4).
    - Xóa thư mục tạm (Auto Cleanup) sử dụng khối `finally`.

### 4. API Endpoints
- **`backend/app/api/routes/download.py`**:
  - `POST /api/v1/download`: Sinh `job_id`, gọi `download_video_task.delay()`, trả về 202 Accepted.
  - `POST /api/v1/download/batch`: Tương tự cho mảng URLs (Batch Foundation).
  - `GET /api/v1/download/{job_id}/events`: Sử dụng `EventSourceResponse` của `sse-starlette`, subscribe Redis channel `job:<job_id>` để đẩy data về Frontend.
  - `GET /api/v1/download/{job_id}`: Fallback API để lấy status cuối.
  - `DELETE /api/v1/download/{job_id}`: Revoke task Celery.
- Cập nhật `main.py` để nhúng router mới.

### 5. Unit & Integration Tests
- Thêm file test `tests/test_download.py` mock Celery `delay` để đảm bảo API endpoints phản hồi đúng cấu trúc.

### 6. Tài Liệu Cập Nhật
- Cập nhật `README.md` hướng dẫn chạy Celery.
- Tạo `PHASE_3_SUMMARY.md`.

---

## Open Questions (Cần bạn duyệt)

1. **Lưu file ở đâu?** Trong Phase 3, mình sẽ lưu file ở thư mục `./downloads` (tạo thư mục tạm) và host một route Static `/static/downloads` để trả link tải file trực tiếp cho người dùng, nhằm phục vụ test E2E. Khi sang Phase 4, mình sẽ thay bằng upload S3 thật. Bạn có đồng ý với thiết kế giả lập này cho Phase 3 không?
2. **FFmpeg:** Bạn xác nhận là máy tính/server của bạn chạy Docker đã sẵn sàng để cài đặt và chạy ngầm FFmpeg bên trong Container nhé?
