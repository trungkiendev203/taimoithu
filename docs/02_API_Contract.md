# API Contract - Tải Mọi Thứ (All-in-One Video Downloader)

**Status:** Approved | **Version:** 1.2.0 | **Date:** 2026-05-30
**Document:** `02_API_Contract.md`

Tài liệu này xác định giao thức giao tiếp giữa Frontend Client (React) và Backend Server (FastAPI) cho hệ thống Tải Mọi Thứ. Contract được thiết kế để triển khai độc lập, hỗ trợ mô hình Event-Driven (giao tiếp qua Server-Sent Events) kết hợp Fallback Polling.

---

## 1. API Contract Overview

- **Mục tiêu:** Thống nhất cách thức truyền tải dữ liệu, cấu trúc request/response, đảm bảo Frontend biết chính xác payload cần gửi và dữ liệu sẽ nhận được.
- **Client (Actor):** Web Browser (Frontend React).
- **Base URL:** `https://api.taimoithu.com/api/v1`
- **Versioning:** URL-based versioning (`/v1/`).
- **Format:** `application/json` cho mọi Request/Response.

---

## 2. Authentication & Authorization

Ở phiên bản V1 (Freemium Model), hệ thống **KHÔNG** sử dụng JWT.

- **Cơ chế xác thực & Rate Limit:** Kết hợp **IP Tracking** (`CF-Connecting-IP`) và **Browser Fingerprint** (Header `X-App-Client-Id`). Việc chia trọng số theo cả IP và Client ID giúp tránh block nhầm người dùng hợp lệ trong môi trường mạng NAT.
- **Quota Limit:** Giới hạn 10 lượt tải/ngày. 
- **Cách xử lý lỗi:** Khi quá giới hạn, server trả về HTTP Status `429 Too Many Requests`.

---

## 3. Common Request Conventions

Tất cả các API calls từ Frontend cần tuân thủ:

- **Headers chuẩn:**
  - `Accept: application/json`
  - `Content-Type: application/json`
  - `X-Request-ID`: Chuỗi UUIDv4 tạo bởi Frontend để Backend dùng cho tracing log.
  - `X-App-Client-Id`: Chuỗi UUIDv4 sinh ra ở lần đầu truy cập trang web và lưu vĩnh viễn ở `localStorage`.
  - `Idempotency-Key`: Dùng cho method `POST` để tránh tạo trùng lặp Job nếu rớt mạng. Nếu backend nhận được key trùng lặp trong 1 giờ, trả về `job_id` cũ với HTTP Status `200 OK` (thay vì `202 Accepted`).
- **Date/Time format:** ISO-8601 kết thúc bằng `Z` (`YYYY-MM-DDThh:mm:ss.sssZ`). Frontend dùng `dayjs` hoặc `date-fns` để parse thống nhất.
- **Null Fields:** Nếu một field không có giá trị, Backend **phải lược bỏ hẳn (omit)** khỏi JSON thay vì trả về `null`.
- **Đơn vị chuẩn:** Mọi dung lượng tính bằng `bytes` (Integer). Mọi thời gian đếm ngược tính bằng `seconds` (Integer).

---

## 4. Common Response Format (Envelope Pattern)

### 4.1 Success Response (`200 OK`, `202 Accepted`)
```json
{
  "status": "success",
  "data": { ... },
  "metadata": {
    "timestamp": "2026-05-30T10:00:00Z",
    "request_id": "frontend-uuid-here"
  }
}
```

### 4.2 Error Response (`4xx`, `5xx`)
```json
{
  "status": "error",
  "error": {
    "code": "ERR_VALIDATION_FAILED",
    "message": "Dữ liệu đầu vào không hợp lệ.",
    "is_retryable": false,
    "details": [ ... ]
  },
  "metadata": { "timestamp": "...", "request_id": "..." }
}
```
*(Lưu ý: `is_retryable` giúp UI biết có nên hiện nút "Thử lại" hay không).*

---

## 5. API Endpoint Specification

### 5.1 System & Session Init (`GET /session/init`)
- **Mục đích:** Gộp chung `config` và `quota`. Lấy trạng thái nền tảng và quota còn lại của Client ID hiện tại.
- **Success Response:**
  ```json
  "data": {
    "platforms": {
      "youtube": { "status": "UP" },
      "facebook": { "status": "DOWN", "message": "Đang bảo trì" }
    },
    "quota": { "used": 3, "limit": 10, "reset_at": "2026-05-31T00:00:00Z" }
  }
  ```

### 5.2 Phân tích URL (`GET /analyze?url=...`)
- **Mục đích:** Lấy thông tin metadata của video (Chuyển sang `GET` để tận dụng CDN Cache).
- **Query Params:** `url` (URI Encoded).
- **Success Response:**
  ```json
  "data": {
    "title": "Never Gonna Give You Up",
    "author_name": "Rick Astley",
    "author_avatar": "https://...",
    "thumbnail_url": "https://...",
    "duration_seconds": 212,
    "formats": [
      { "format_id": "bestvideo+bestaudio", "quality_label": "1080p", "type": "video", "has_audio": true, "has_video": true, "video_codec": "avc1", "estimated_size_bytes": 45500000 }
    ]
  }
  ```

### 5.3 Tạo Job Tải Đơn Lẻ (`POST /download`)
- **Request Body:** `{ "url": "https://...", "format_id": "bestvideo+bestaudio" }`
- **Success Response (202 Accepted):** 
  ```json
  "data": {
    "job_id": "uuid-job-123",
    "estimated_processing_time_sec": 45
  }
  ```

### 5.4 Tạo Job Tải Hàng Loạt (`POST /download/batch`)
- **Request Body:** 
  ```json
  {
    "urls": ["https://tiktok.com/1", "https://tiktok.com/2"],
    "type": "video",
    "quality_preference": "1080p"
  }
  ```
- **Success Response (202 Accepted):** `{"job_id": "uuid-batch-456", "estimated_processing_time_sec": 120}`

### 5.5 SSE Lắng nghe Tiến Độ (`GET /download/{job_id}/events`)
- **Luồng dữ liệu (Stream Data):**
  ```text
  event: status
  data: {"job_id": "123", "status": "PROCESSING", "progress": 15, "speed_bytes": 1258291, "downloaded_bytes": 1048576, "total_bytes": 10485760, "eta_seconds": 25}

  event: status
  data: {"job_id": "123", "status": "FAILED", "error_code": "ERR_YTDLP_EXTRACT", "error_message": "Video is private."}

  event: completed
  data: {"job_id": "123", "status": "COMPLETED", "download_url": "https://r2..."}
  ```
- **Lưu ý S3 Link:** Presigned URL phải có `response-content-disposition=attachment`. Thời gian sống (TTL) của link phải thiết lập là **1 giờ (3600s)** để đảm bảo tải file lớn không bị đứt.

### 5.6 Get Job Status Fallback (`GET /download/{job_id}`)
- **Mục đích:** API Long-polling khi SSE bị chặn.

### 5.7 Lấy Danh Sách Tải Gần Đây (`GET /download/recent`)
- **Mục đích:** Dành cho SEO Landing Page, khi user F5 lại trang có thể thấy các file vừa tải trong phiên (`X-App-Client-Id` hiện tại).

### 5.8 Hủy Job Đang Tải (`DELETE /download/{job_id}`)
- **Mục đích:** Hủy tiến trình FFmpeg/Zipping đang chạy ngầm trên Server để tiết kiệm tài nguyên.
- **Success Response:** Trả về `200 OK` (Nếu thành công) hoặc `409 Conflict` (Nếu job đã hoàn thành từ trước).

### 5.9 Báo Cáo Lỗi Từ Client (`POST /logs/client`)
- **Mục đích:** Ghi nhận lỗi khi Frontend parse SSE thất bại hoặc S3 download bị CORS/Network Error.
- **Request Body:** `{ "error_context": "SSE_PARSE_ERROR", "raw_message": "...", "job_id": "..." }`

---

## 6. Data Transfer Objects (DTOs)

| DTO Name | Field | Type | Description |
| :--- | :--- | :--- | :--- |
| **FormatDTO** | `has_audio`, `has_video` | bool | Cờ đánh dấu video câm hay audio only. |
| | `estimated_size_bytes` | int | Dung lượng ước tính (Bytes). |
| **SSEEventDTO** | `status` | enum | PENDING, PROCESSING, MERGING, ZIPPING, COMPLETED, FAILED. |
| | `eta_seconds` | int | Thời gian hoàn thành dự kiến. |
| | `error_code`, `error_message` | str | CHỈ có khi status = FAILED. |
| **ErrorWrapper**| `is_retryable` | bool | Cờ báo cho Frontend hiển thị nút Retry. |

---

## 7. Frontend Integration Notes

- **Cache Invalidation:** `/analyze` là API GET nên dùng React Query. Cache staleTime có thể set khoảng 5 phút vì link video thay đổi format liên tục.
- **Zombie SSE:** Bắt buộc phải gọi `eventSource.close()` khi component React unmount hoặc khi bắt được event `COMPLETED`/`FAILED`.
- **Optimistic UI:** Đối với luồng Batch (tải mất thời gian nén), UI cần thiết kế màn hình loading "Zipping" có animation mượt mà (chạy % ảo hoặc loop animation) để tránh việc màn hình bị đơ quá lâu.

---

## 8. Backend Implementation Notes

- **Async Redis:** BẮT BUỘC sử dụng `redis.asyncio` khi listen Pub/Sub.
- **Idempotency Lock:** Dùng `SETNX` trên Redis, phải bắt `LockTimeout` cẩn thận để không văng HTTP 500 khi user bấm 2 lần quá nhanh.
- **N+1 Redis Query:** API `GET /download/recent` phải dùng lệnh `MGET` hoặc Pipeline trên Redis để lấy trạng thái 10 jobs cùng lúc, tránh bị N+1 reads.

---

## 9. Security Considerations

- **DDoS qua SSE:** Bổ sung TTL 30 phút tự ngắt kết nối cho Endpoint `/events`. Limit kết nối đồng thời từ 1 IP ở mức Nginx.
- **IP NAT Friendly Rate Limiting:** Rate limit giờ đây dựa vào `X-App-Client-Id`.
- **Bảo mật URL (SSRF):** Chặn SSRF bằng DNS Resolution.
