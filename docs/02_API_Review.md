# 02_API_Review.md - Khảo Sát Thiết Kế Giao Tiếp API

**Role:** Principal Backend Engineer, Staff Frontend Engineer, API Governance Reviewer
**Document Under Review:** `02_API_Contract.md` (v1.1.0)
**Date:** 2026-05-30

---

## 1. Executive Summary

Bản API Contract v1.1.0 đã có những cải thiện xuất sắc so với phiên bản trước, đặc biệt là việc sử dụng Envelope Pattern thống nhất (`status`, `data`, `metadata`), bổ sung API config, và xử lý Rate Limit dựa trên Client ID. Giao thức Server-Sent Events (SSE) đã được mô tả chi tiết, giải quyết bài toán UI/UX theo thời gian thực.

**Đánh giá chung:** 
- API đã đạt mức **75% sẵn sàng** để Frontend và Backend có thể code độc lập. 
- Vẫn còn một số endpoint bị thiếu cho flow vận hành thực tế (Hủy tải, Lấy lịch sử tải ngắn hạn theo Session). 
- Response format khá nhất quán nhưng còn một số trường kiểu dữ liệu chưa đồng nhất (Ví dụ: `estimated_size_mb` nên đổi thành bytes để nhất quán với `speed_bytes`).
- Có một vài rủi ro liên quan đến việc Frontend xử lý cache nếu Backend thay đổi cấu trúc URL Analyze.

---

## 2. Missing API Review

Dựa trên PRD và Technical Design, đây là các API vẫn đang bị khuyết thiếu:

| Missing API | Purpose | Who Calls It | Why Needed | Suggested Method & Path | Priority |
| ----------- | ------- | ------------ | ---------- | ----------------------- | -------- |
| **Cancel Job** | Hủy tiến trình tải (đặc biệt là Batch) đang chạy | Frontend | User bấm tải nhầm file nặng, hoặc đổi ý, muốn hủy để không tốn quota và tài nguyên server. | `DELETE /download/{job_id}` | High |
| **Client Error Report** | Gửi log lỗi từ Frontend về Backend | Frontend | Frontend bắt được exception khi parse SSE hoặc khi S3 Presigned URL bị lỗi (CORS, 403) nhưng Backend không hề biết. | `POST /logs/client` | Medium |
| **Recent Downloads** | Lấy danh sách 5 file vừa tải xong của Client đó | Frontend | PRD v2 có tính năng SEO Landing. Khi user F5, họ nên thấy lại các file vừa hoàn thành trong phiên làm việc hiện tại để tải lại (Dựa vào `X-Client-ID`). | `GET /download/recent` | Low |

---

## 3. Endpoint Completeness Review

Kiểm tra chi tiết các endpoint hiện tại:

| Endpoint | Finding | Severity | Recommendation |
| -------- | ------- | -------- | -------------- |
| `POST /analyze` | **Method không chuẩn REST:** Analyze là thao tác *Read-only*, Idempotent và có thể Cache. Dùng POST làm mất khả năng cache ở tầng CDN/Nginx. | Medium | Đổi thành `GET /analyze?url=...` |
| `POST /download/batch` | **Resource modeling hơi lệch:** Hành động batch tải hàng loạt vẫn tạo ra một Job. Đặt `/download/batch` là hợp lý nhưng payload thiếu tham chiếu `format_id` cụ thể nếu user muốn ép chất lượng 720p. | Low | Bổ sung optional field `quality_preference: "1080p" | "720p"` bên cạnh `type`. |
| `GET /quota` | **Endpoint quá specific:** Quota thực chất là thuộc tính của User Session (Client). Mở một endpoint riêng chỉ trả về 3 field là hơi phí tài nguyên connection. | Low | Gộp `quota` vào chung với response của `GET /config` (Đổi tên thành `GET /session/init`). |

---

## 4. Response Consistency Review

Kiểm tra tính nhất quán trên toàn bộ DTOs:

| Area | Current Issue | Example | Expected Standard | Severity |
| ---- | ------------- | ------- | ----------------- | -------- |
| **Size Unit Format** | Bất nhất đơn vị đo lường. SSEEventDTO dùng `bytes` (`speed_bytes`), nhưng FormatDTO lại dùng `MB` (`estimated_size_mb`). | `estimated_size_mb: 45.5` | Phải chuẩn hóa dùng `bytes` trên toàn hệ thống (VD: `estimated_size_bytes`). Trách nhiệm format `MB/GB` thuộc về Frontend. | High |
| **Null vs Omitted** | Không rõ quy tắc trả về các trường Null. | `download_url` chỉ có khi COMPLETED | Nếu field không có giá trị, Backend trả về `null` hay *lược bỏ hẳn* (omit) khỏi JSON? (Khuyến nghị: Lược bỏ hẳn để JSON gọn nhẹ). | Medium |
| **Date/Time** | Thiếu timezone explicit. | `2026-05-30T10:00:00Z` | Chuẩn ISO-8601 kết thúc bằng `Z` là tốt, nhưng cần thống nhất Frontend dùng thư viện nào để parse (dayjs/date-fns). | Low |

---

## 5. Response Schema Review

| Endpoint | Missing/Problematic Field | Impact on Frontend | Recommendation |
| -------- | ------------------------- | ------------------ | -------------- |
| `POST /analyze` | Thiếu `platform_logo` và `author`. | Frontend phải tự hardcode logo dựa vào field `platform`. Thiếu tên tác giả video làm UI trống trải. | Bổ sung `author_name` và `author_avatar` vào metadata trả về. |
| `GET /events` | Thiếu `eta_seconds`. | Hiện tại `eta` đang bị define là string ngầm định. Cần format chuẩn. | Thêm `eta_seconds` (Integer) để Frontend tự render "12 giây trước", "1 phút trước". |
| `POST /download` | Response thiếu `estimated_time`. | User bấm tải xong chỉ thấy PENDING, không biết sẽ mất 5 giây hay 5 phút. | Backend dự đoán trả về `estimated_processing_time_sec` dựa trên dung lượng. |

---

## 6. Error Response Review

Format hiện tại:
```json
{
  "status": "error",
  "error": { "code": "ERR_...", "message": "...", "details": [] }
}
```
**Nhận xét & Rủi ro:**
- Cấu trúc rất chuẩn và chuyên nghiệp. 
- Tuy nhiên, **Chưa phân biệt Retryable**. Frontend không biết lỗi nào thì nên thử lại (ví dụ mạng chập chờn, yt-dlp timeout) và lỗi nào thì vĩnh viễn (video bị xóa).
- **Khuyến nghị:** Thêm trường `is_retryable: boolean` vào trong object `error`. Nếu `true`, Frontend có thể hiện nút "Thử lại". Nếu `false`, disable nút.

---

## 7. Frontend Integration Risk

- **Rủi ro Zombie SSE:** Khi component React unmount (user chuyển trang), nếu quên gọi `eventSource.close()`, trình duyệt sẽ vĩnh viễn giữ connection đó, gây Memory Leak và ngốn Connection Limit.
- **Cache Invalidation:** Endpoint `/analyze` nếu đổi thành `GET`, Frontend dùng React Query sẽ dễ dàng cache. Nhưng thời gian sống của cache (staleTime) phải set cực thấp (vd: 5 phút) vì các token trong video URL của YouTube/TikTok thay đổi liên tục.
- **Optimistic UI:** Flow Batch tải tốn thời gian zipping. Trong lúc đó, user không thấy từng file hoàn thành mà phải chờ cả cục ZIP. Sẽ rất nhàm chán. Cần có animation hiển thị ảo (Optimistic).

---

## 8. Backend Implementation Risk

- **Rủi ro N+1 Celery Status:** Nếu API `GET /download/{job_id}` (Fallback) gọi trực tiếp vào Redis để đọc status của 1 Job thì nhanh, nhưng nếu sau này có API `GET /download/recent` lấy 10 jobs, backend sẽ dính N+1 read từ Redis (phải dùng pipeline hoặc MGET).
- **Idempotency Bypass:** Nếu user gửi 2 request `/download` cùng lúc tính bằng miliseconds, Redis `SETNX` có thể bắt được, nhưng nếu FastAPI không xử lý `LockTimeout` cẩn thận, request thứ 2 sẽ quăng HTTP 500 thay vì HTTP 200 + old_job_id.
- **S3 Presigned URL Expiration:** Thời gian 15 phút là rất ngắn đối với file 2GB (người dùng mạng chậm tải mất 30 phút). Nếu link S3 hết hạn giữa chừng khi đang tải, user bị đứt mạng. Cần tăng lên 1 giờ.

---

## 9. Standardization Recommendations

Để Document hoàn hảo 100%, Backend và Frontend cần thống nhất các chuẩn sau:
1. **Size/Duration:** Mọi dung lượng tính bằng `bytes` (Integer). Mọi thời gian đếm ngược tính bằng `seconds` (Integer). KHÔNG DÙNG string ("45MB", "12s").
2. **Boolean Naming:** Các cờ boolean phải bắt đầu bằng `is_`, `has_`, `should_` (VD: `has_audio`, `is_retryable`).
3. **Empty Fields:** Trả về Array rỗng `[]` thay vì `null` cho danh sách. Lược bỏ hẳn key (Omit) đối với các chuỗi/object nếu bị `null`.
4. **Header Format:** Header tùy chỉnh luôn có tiền tố `X-App-` (Đổi `X-Client-ID` thành `X-App-Client-Id` để không bị đụng hàng với WAF proxy).

---

## 10. Final Findings

| Category | Finding | Severity | Impact | Required Fix |
| -------- | ------- | -------- | ------ | ------------ |
| Missing API | Thiếu API `DELETE /download/{job_id}` để hủy tải. | High | Gây lãng phí tài nguyên Server khi user không còn cần file. | Bổ sung API Hủy. |
| Inconsistency| Đơn vị Size/Time bị dùng lẫn lộn giữa string và int. | High | Frontend phải viết code parse chuỗi dễ gây bug. | Đổi hết về `bytes` và `seconds`. |
| API Design | `/analyze` dùng POST làm mất khả năng CDN Cache. | Medium | Tăng tải cho backend. | Chuyển sang `GET` (pass url qua query param encoded). |
| Error Handing| Thiếu cờ `is_retryable` trong Error object. | Medium | UI khó xử lý luồng lỗi tự động. | Thêm cờ vào Error Wrapper. |
| Operational | S3 Link hết hạn quá nhanh (15 phút). | High | User mạng chậm tải file to bị đứt gãy. | Tăng Presigned URL expiry lên 1 tiếng. |

---

## 11. Final Scores

- **API Completeness Score:** 8.0 / 10
- **Response Consistency Score:** 7.5 / 10
- **Frontend Readiness Score:** 8.5 / 10
- **Backend Readiness Score:** 8.0 / 10
- **Error Handling Score:** 8.5 / 10
- **Contract Clarity Score:** 9.0 / 10
- **Production Readiness Score:** **8.3 / 10**

---

## 12. Final Verdict

⚠️ **Approved with Minor Changes**

**Giải trình:** 
Contract Design đã đạt chuẩn Production ở phần khung sườn kiến trúc. Mọi ngóc ngách về Rate Limit, SSE, Envelope Pattern đều được xử lý sắc bén. 

Chỉ cần cập nhật, sửa nhẹ (Minor Changes) các chuẩn Format theo đúng như khuyến nghị ở phần `9. Standardization Recommendations` (chuyển size về bytes, time về seconds, đổi analyze sang GET) và bổ sung API Hủy Job là hệ thống hoàn toàn có thể bắt tay vào Sprint Coding đầu tiên.
