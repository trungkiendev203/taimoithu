# 🔬 Khảo sát và Đánh giá API Contract (Executive Review)

**Review Panel:** Principal Backend Engineer, Staff Frontend Engineer, Solution Architect, API Governance Reviewer
**Document Under Review:** `02_API_Contract.md` (v1.0.0)
**Date:** 2026-05-30

---

## Executive Summary

Tài liệu API Contract đã phác thảo khá rõ ràng giao thức giao tiếp giữa Frontend và Backend. Cấu trúc JSON Envelope (gói dữ liệu trong `status`, `data`, `metadata`) rất chuyên nghiệp. Việc quyết định sử dụng Server-Sent Events (SSE) để đẩy tiến trình tải (progress) phản ánh đúng tư duy xây dựng hệ thống bất đồng bộ, giúp tiết kiệm tài nguyên so với Polling.

Tuy nhiên, với con mắt khắt khe của hệ thống Production, tài liệu này vẫn còn nhiều lỗ hổng về mặt thiết kế chi tiết (Micro-design). Các nguy cơ chính đến từ việc thiếu hụt API hỗ trợ (fallback, health check), thiết kế Payload cho SSE thiếu tính mở rộng, và format dữ liệu chưa tối ưu cho Frontend (trả về string thay vì raw number cho speed). Nếu triển khai ngay, Frontend và Backend chắc chắn sẽ phải họp lại nhiều lần trong quá trình code để vá lỗi contract.

---

## Bảng Chi Tiết Vấn Đề (Detailed Findings)

| Category | Finding | Severity | Impact | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| **API Design** | **Thiếu API Get Status (Fallback):** Chỉ có SSE. Nếu proxy/firewall mạng công ty/nhà trường của user chặn SSE (block long-lived HTTP connection), user không có cách nào biết tiến độ. | High | Một tập user nhất định (sau firewall) không thể tải được file do UI bị treo. | Bổ sung API `GET /download/{job_id}` trả về status hiện tại làm cơ chế fallback (Long-polling) cho Frontend khi SSE thất bại. |
| **API Design** | **Thiếu API Platform Health & Quota:** PRD yêu cầu có "Platform Health Badge", nhưng API Contract không có API nào trả về trạng thái các nền tảng (cái nào đang sống/chết) và số lượt tải còn lại của user. | High | Frontend phải hardcode UI, không biết user còn bao nhiêu lượt để hiển thị cảnh báo chặn trước khi tải. | Bổ sung API `GET /config` (hoặc `/health/platforms`) và `GET /quota` để FE render UI linh hoạt. |
| **Response Contract** | **SSE Payload thiếu trường `error`:** Enum status có `FAILED`, nhưng event FAILED không hề có trường mô tả lý do lỗi (do video private, do hết quota hay do lỗi hệ thống). | High | Frontend chỉ có thể báo "Lỗi" chung chung, trải nghiệm người dùng (UX) rất tệ. | Bổ sung trường `error_code` và `error_message` vào DTO của SSE Event (chỉ xuất hiện khi status = FAILED). |
| **Response Contract** | **Format dữ liệu `speed` sai chuẩn:** Backend trả về `speed: "1.2MB/s"` (String). Đây là lỗi kinh điển. Backend không nên làm việc format UI. | Medium | Frontend không thể convert lại thành số để vẽ biểu đồ tốc độ hoặc tự format theo ngôn ngữ (Locale) của user (ví dụ user Pháp thích "1,2 Mo/s"). | Đổi trường `speed` thành `speed_bytes_per_second` (Integer) và `downloaded_bytes` (Integer). Việc format để Frontend lo. |
| **Request Contract** | **Batch Download Request mơ hồ:** Payload yêu cầu `format_preference: "best"`. Nhưng "best" là best audio hay best video? Làm sao user chọn tải toàn bộ file MP3 trong 1 playlist 5 bài? | Medium | Backend và Frontend sẽ code lệch nhau, tính năng batch download bị giới hạn chỉ ở "best video". | Thay `format_preference` bằng `type: "video" | "audio"`. Backend sẽ tự động lấy format_id "bestvideo+bestaudio" hoặc "bestaudio" tương ứng cho toàn bộ link. |
| **Scalability** | **Giới hạn IP NAT:** Rate Limit 10 lượt/IP/ngày. Rất nhiều user ở chung 1 tòa nhà/công ty/quán net dùng chung 1 IP Public (NAT). 1 người tải sẽ làm 99 người còn lại bị block. | High | Lượng lớn user thật bị false-positive rate limit. | Kết hợp IP Tracking + Browser Fingerprint (UUID lưu ở LocalStorage gửi qua Header `X-Client-ID`). Rate limit chia đôi trọng số cho cả 2 để công bằng hơn. |
| **Response Contract** | **Thiếu Content-Disposition cho S3 Presigned URL:** Khi báo `COMPLETED`, API trả về `download_url`. Nếu S3 không được cấu hình ép tải (force download), trình duyệt sẽ *play video* trên tab mới thay vì *tải về máy*. | Critical | User bấm tải nhưng video lại tự động phát, gây ức chế lớn, tốn băng thông S3 mà không đạt mục đích. | Backend khi tạo Presigned URL bắt buộc phải inject tham số `response-content-disposition=attachment; filename="tieu_de_video.mp4"`. (Cần note rõ vào contract). |
| **Frontend Integration**| **Batch Download Progress quá sơ sài:** Tiến trình nén ZIP có status `ZIPPING` nhưng khi đang tải 5 file thì status là gì? Trả về 1 progress chung 0-100% cho 5 file rất khó làm mượt. | Medium | Progress bar trên giao diện nhảy giật cục, user tưởng bị đơ máy. | Thêm trường `batch_details: { current_file: 2, total_files: 5 }` vào SSE Payload khi xử lý luồng Batch. |
| **Consistency** | **Thiếu Document về Idempotency:** Common Headers có nhắc đến `Idempotency-Key` nhưng các endpoints không hề define cách xử lý (trả về 200 OK + job_id cũ hay 409 Conflict?). | Low | Frontend gửi lại request do rớt mạng có thể tạo ra 2 job giống nhau, tốn tài nguyên worker. | Define rõ hành vi: Nếu gọi `/download` với `Idempotency-Key` trùng lặp trong 1 giờ, trả về `job_id` cũ kèm HTTP Status 200 thay vì 202. |
| **Security** | **DDoS thông qua SSE Connections:** Một attacker mở 10,000 tab để giữ 10,000 kết nối SSE `/events`. Server FastAPI cạn kiệt Worker/Socket. | High | Sập hệ thống API Gateway. | Bổ sung giới hạn thời gian sống (TTL) cho một kết nối SSE (ví dụ: tối đa 30 phút tự ngắt). Giới hạn số lượng SSE Connection / IP ở tầng Nginx/Cloudflare. |

---

## Missing APIs (Các API cần bổ sung)

1. `GET /api/v1/download/{job_id}`: Lấy trạng thái hiện tại của job (dùng làm fallback khi SSE không hoạt động hoặc khi user F5 tải lại trang).
2. `GET /api/v1/config` (hoặc `/health`): Trả về cấu hình hệ thống bao gồm danh sách các platform đang hoạt động (để UI disable các nút nền tảng bị lỗi).
3. `GET /api/v1/quota`: Trả về thông tin giới hạn hiện tại của IP/Client (`{"used": 3, "limit": 10}`).

---

## Missing Fields (Các trường cần bổ sung vào DTO)

1. **Trong SSEEventDTO:**
   - Bổ sung `error_code` (string) và `error_message` (string) (Chỉ xuất hiện khi status là FAILED).
   - Đổi `speed` (string) thành `speed_bytes` (integer).
   - Thêm `downloaded_bytes` (integer) và `total_bytes` (integer).
   - Thêm `batch_current` (int) và `batch_total` (int) (Chỉ dùng cho tiến trình Batch).
2. **Trong FormatDTO (Response của `/analyze`):**
   - Thêm `has_audio` (boolean) và `has_video` (boolean) (để Frontend biết format này là video câm, audio only, hay video đủ tiếng).
   - Thêm `video_codec` và `audio_codec` (tùy chọn, để phục vụ người dùng pro).

---

## Frontend Risks (Rủi ro tích hợp giao diện)

* **Progress Bar "Giật Lùi":** Khi Frontend bị đứt kết nối mạng trong 5 giây, trình duyệt tự reconnect EventSource. Nếu Backend không lập tức gửi ngay bản tin progress mới nhất (last known state) khi connection vừa mở, Frontend sẽ phải đợi đến khi có progress nhích thêm thì UI mới update.
* **Xử lý `onmessage` không đủ:** Cần lưu ý Frontend chỉ được ngắt SSE (`.close()`) khi nhận được các Terminal States (`COMPLETED`, `FAILED`). Nếu ngắt sớm, Job vẫn chạy ngầm nhưng user không nhận được file.

---

## Backend Risks (Rủi ro triển khai server)

* **Quá tải Event Loop do Redis Pub/Sub:** Nếu sử dụng thư viện Redis sync để listen Pub/Sub trong endpoint SSE của FastAPI, toàn bộ server sẽ bị block. Phải đảm bảo dùng thư viện Async Redis (như `redis.asyncio`) kết hợp `sse-starlette`.
* **Idempotency logic:** Phải implement cẩn thận cache lock trên Redis đối với `Idempotency-Key` để không sinh ra 2 Celery Task trùng nhau khi Frontend retry request.

---

## Production Risks (Rủi ro vận hành)

* **Cạn kiệt File Descriptor (FD):** Do dùng SSE (Long-lived HTTP Connection), mỗi client kết nối sẽ giữ 1 socket. Cần tune cấu hình OS của server chạy FastAPI (tăng `ulimit -n`) và cấu hình Timeout, nếu không server sẽ báo `Too many open files`.
* **Hành vi phát video của trình duyệt:** Nhấn mạnh lại, nếu presigned URL không có header `Content-Disposition: attachment; filename="xyz.mp4"`, 99% trình duyệt hiện đại sẽ mở trình phát video thay vì tải xuống.

---

## Final Scores

* **API Design Score:** 6.5/10 *(Thiếu API Fallback và Quota, lạm dụng chuỗi string ở field cần tính toán).*
* **Contract Clarity Score:** 8.0/10 *(Document viết dễ hiểu, có JSON mẫu rõ ràng).*
* **Frontend Readiness Score:** 7.0/10 *(Frontend sẽ gặp khó khi làm Batch Progress và Error Handling).*
* **Backend Readiness Score:** 7.5/10 *(Backend dễ implement nhưng sẽ phải sửa lại DTO).*
* **Security Score:** 7.0/10 *(Rủi ro DDoS qua SSE, rủi ro Rate Limit false-positive với NAT IP).*
* **Scalability Score:** 7.0/10 *(SSE Connection limits chưa được handle ở thiết kế).*
* **Maintainability Score:** 8.5/10 *(Envelope pattern và Versioning rất tốt).*

---

## Final Verdict

⚠️ **APPROVED WITH MINOR CHANGES**

**Lý do:** Khung sườn kiến trúc API (RESTful kết hợp SSE) đã đúng hướng và vững chắc. Tuy nhiên, các lỗi sai ở chi tiết (Payload fields, thiều API hỗ trợ, logic Rate Limit, ép tải file từ S3) nếu không sửa ngay từ đầu sẽ gây đứt gãy trải nghiệm người dùng nghiêm trọng.

**Hành động bắt buộc (Action Items) trước khi code:**
1. Sửa DTO của `SSEEventDTO`: Chuyển `speed` thành số liệu thô (bytes), bổ sung trường `error` cho FAILED state.
2. Thêm API `GET /download/{job_id}` làm fallback polling.
3. Fix chuẩn tạo Presigned URL: Phải inject `Content-Disposition`.
4. Viết rõ chiến lược cấp số nhân rate limit dựa trên Browser Fingerprint (`X-Client-ID`) kết hợp IP.
