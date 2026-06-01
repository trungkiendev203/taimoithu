# Tóm Tắt Triển Khai Backend (Phase 3)

## Những Gì Đã Làm (Phase 3)
1. **Message Broker**: Tích hợp Redis để làm Broker cho Celery và làm nơi lưu trữ tạm trạng thái (JobState) cũng như Pub/Sub Events.
2. **Background Worker**: Khởi tạo `celery_app.py`, cấu hình worker xử lý tiến trình download độc lập (không làm treo API).
### 2. Xử lý logic tải xuống với Celery Worker (Backend)
- [x] Tiếp nhận `item_index` từ request để chỉ định đúng item cần tải trong Playlist/Carousel.
- [x] Truyền `playlist_items=str(item_index)` vào `yt-dlp` options.
- [x] Cập nhật hàm xử lý tiến trình để publish WebSocket message chính xác theo `job_id`.
- [x] **Xử lý ngoại lệ cho Instagram**: Bắt lỗi `ExtractorError` ("No video formats found") và trả về lỗi thân thiện cho UI thay vì crash worker.

### 3. Cập nhật `ytdlp_service.py` (Backend API)
- [x] Truyền cookies vào `extract_info` cho Instagram để đọc metadata các bài post private/carousel.
- [x] Xử lý lỗi `yt-dlp` trả về danh sách 12 items trùng lặp cho single post bằng cách **deduplicate entries** theo `id` và `url`.
- [x] Bỏ qua lỗi `ignore_no_formats_error=True` để có thể extract được thông tin cơ bản cho các bài thuần ảnh.

4. **API Mới Thêm**:
   - `POST /api/v1/download`: Submit link và nhận lại `job_id` (trả về 202 Accepted).
   - `GET /api/v1/download/{job_id}`: Lấy trạng thái thủ công (Polling).
   - `GET /api/v1/download/{job_id}/events`: Lắng nghe kết nối liên tục SSE (Server-Sent Events) để frontend vẽ Progress Bar thời gian thực.
5. **Static File Fake S3**: Phục vụ E2E test bằng cách mount thư mục `downloads` thành static API `/static/downloads/...`.
6. **Docker Compose**: Nâng cấp bao gồm 3 services đồng bộ: `api` (FastAPI), `redis` (Cache/Broker), `worker` (Celery).

## Cách Chạy Local (Môi Trường Development)

Cách đơn giản nhất là dùng Docker:
```bash
docker-compose up --build
```
Hệ thống sẽ chạy:
- FastAPI tại `http://localhost:8000`
- Redis tại port `6379`
- Celery worker chạy ngầm, theo dõi log ở cửa sổ terminal.

Nếu chạy trực tiếp (không dùng Docker):
1. Cài đặt và bật sẵn Redis Server (hoặc Docker chạy riêng Redis).
2. Sửa `REDIS_URL` trong `.env` thành `redis://localhost:6379/0`.
3. Bật API ở Terminal 1: `uvicorn app.main:app --reload`.
4. Bật Worker ở Terminal 2: `celery -A app.core.celery_app worker --loglevel=info -P solo` (trên Windows dùng `solo`).

## Những Gì Còn Lại Cho Phase 4
1. Cắm tích hợp Storage thật sự (S3/Cloudflare R2/MinIO) để thay thế thư mục `/downloads` nội bộ.
2. Thêm logic xóa thư mục tạm sau khi Upload S3 thành công.
3. Đấu nối Database (PostgreSQL) thật để quản lý Quota/User Account thay vì chỉ lưu tạm trên Redis.
