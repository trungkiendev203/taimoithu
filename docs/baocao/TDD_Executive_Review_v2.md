# 🔬 Technical Design Review: "Tải Mọi Thứ" TDD v1.0

**Reviewer Role:** Principal Engineer / Staff Software Engineer / Solution Architect
**Document:** 01_Technical_Design_Document.md
**Date:** 2026-05-30
**Objective:** Đánh giá toàn diện kiến trúc, xác định bottleneck, rủi ro production và lỗ hổng thiết kế trước khi bắt đầu Sprint 1.

---

## 1. Executive Summary

Tài liệu TDD v1.0 đã phác thảo được hình hài của một hệ thống xử lý video bất đồng bộ (FastAPI + Redis + Celery), phù hợp với yêu cầu tải nặng và kéo dài. Việc phân tách rõ "Queue Nhanh" (Direct stream) và "Queue Chậm" (FFmpeg) cho thấy sự hiểu biết nhất định về đặc thù bài toán.

Tuy nhiên, tài liệu hiện tại đang mắc phải **nhiều lỗ hổng nghiêm trọng ở tầng thiết kế chi tiết (Low-level Design)**. Nghiêm trọng nhất là sự nhập nhằng trong cơ chế truyền tải file từ Celery Worker về Client, rủi ro lớn về Data Inconsistency với SQLite trong môi trường đa luồng, và lỗ hổng bảo mật SSRF chưa được xử lý triệt để. Hệ thống thiết kế theo kiểu "Micro-Monolith" nhưng lại phụ thuộc vào Local File System (`/tmp`), điều này sẽ chặn đứng hoàn toàn khả năng mở rộng ngang (Horizontal Scaling) trong tương lai.

**Trạng thái hiện tại không đủ điều kiện để bắt đầu code (Not Implementation-Ready).**

---

## 2. Các Lỗ Hổng & Rủi Ro Phát Hiện (Detailed Findings)

| Category | Finding | Severity | Impact | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| **Architecture / Data Flow** | **Không có đường dẫn dữ liệu từ Celery về FastAPI Client:** Celery là task queue bất đồng bộ. FastAPI giữ HTTP connection. Khi Celery dùng FFmpeg merge xong file ra `/tmp`, làm sao FastAPI biết để stream về client? TDD hoàn toàn bỏ trống đoạn nối này. | Critical | Dev không thể code được luồng tải. Nếu Celery và FastAPI nằm ở 2 server khác nhau, FastAPI không thể truy cập `/tmp` của Celery. Hệ thống gãy luồng tải cơ bản nhất. | Thiết kế lại cơ chế Delivery: Celery merge xong -> Update Redis Pub/Sub -> FastAPI nhận signal qua SSE -> Client gọi API `GET /stream` (Cần Shared Volume/S3 giữa API và Worker, KHÔNG dùng `/tmp` cục bộ). |
| **Concurrency / DB** | **Race Condition & Lock với SQLite:** Dùng SQLite cho hệ thống bất đồng bộ có nhiều Celery Workers cùng Read/Write (cập nhật status liên tục). | High | `database is locked` error liên tục. Cập nhật status bị mất, tiến trình tải bị treo không thông báo cho client. Giới hạn khả năng scale. | Đổi ngay sang PostgreSQL cho V1, hoặc chỉ dùng Redis để tracking Job State (vì Redis single-threaded, atomic), SQLite chỉ dùng để lưu quota IP cuối ngày. |
| **Security** | **SSRF Prevention bằng Regex là vô dụng:** Chặn IP nội bộ bằng regex không chống được DNS Rebinding, IPv6 (ví dụ `::1`), hoặc các URL rút gọn redirect HTTP 302 về localhost. | Critical | Hacker có thể chiếm quyền đọc cloud metadata, gọi API nội bộ, hoặc scan mạng LAN của server chứa Celery Worker. | 1. Resolve DNS của URL trước khi pass cho `yt-dlp`. Kiểm tra IP thực tế sau resolve. <br>2. Block HTTP Redirects trong HTTP Client nội bộ. <br>3. Chạy `yt-dlp` trong một Docker container/network namespace không có quyền truy cập LAN (Sandbox). |
| **Data Consistency / Storage** | **Local Storage (`/tmp`) chặn Horizontal Scaling:** TDD đang giả định API và Worker chạy chung 1 máy (Monolith). Khi traffic x10, x100, buộc phải tách riêng Worker Nodes. Lúc này `/tmp` ở Worker A không thể được đọc bởi API Server B. | High | Không thể scale ngang khi bị thắt cổ chai CPU. | Bắt buộc dùng Shared Object Storage (MinIO/S3) hoặc NFS mount cho file tạm. Worker lưu lên S3, API tạo Presigned URL cho Client tải trực tiếp, giảm tải băng thông cho server. |
| **Failure Recovery** | **Race Condition trong Cleanup Service:** Cronjob xóa file > 30 phút. Nếu một file 1080p 2 tiếng đang được FFmpeg xử lý đến phút 31, cronjob sẽ xóa mất file nguồn của nó. | High | Tỷ lệ fail cao với các video dài, khó debug (mất file giữa chừng). | Xóa logic Cronjob quét giờ. Mỗi Celery Task phải chịu trách nhiệm dọn dẹp file của chính nó trong block `finally`. Cronjob chỉ quét các file > 3 giờ (Orphan files). |
| **API Design** | **Thiếu API Download Đơn Lẻ:** Chỉ có API `batch` và `stream`, nhưng use-case 90% là tải 1 file. | Medium | Frontend phải gói 1 URL vào array để gọi batch, làm tăng độ phức tạp không cần thiết. | Bổ sung `POST /api/v1/download` chuyên cho single download, trả về thẳng connection SSE/Stream thay vì tạo Batch_ID. |
| **Performance** | **Blocking Event Loop trong FastAPI:** Gọi `yt-dlp.extract_info()` là thao tác synchronous, tốn từ 2-10 giây. Gọi trực tiếp trong FastAPI sẽ block toàn bộ async event loop. | High | 1 request analyze sẽ làm nghẽn toàn bộ server, các user khác không thể load trang. Xóa bỏ hoàn toàn ưu thế của FastAPI. | Chạy `yt-dlp` thông qua `asyncio.to_thread()` hoặc ThreadPoolExecutor. |
| **Operability** | **OOM (Out Of Memory) Risk khi FFmpeg chạy:** TDD ghi giới hạn 2 concurrent jobs nhưng không có config memory limit (cgroups) hay fallback. | High | FFmpeg ngốn RAM đột biến có thể làm crash toàn bộ Server VPS (OOM Killer giết tiến trình bừa bãi). | Cấu hình Celery `--concurrency=2` kết hợp `max_tasks_per_child=10` (tránh memory leak). Chạy worker trong Docker có set `--memory`. |
| **Requirements** | **Thiếu tính năng từ PRD:** Thiếu chiến lược nén ZIP cho Batch Download, thiếu Popup cảnh báo iOS Safari, thiếu SEO routing. | Low | Không đáp ứng đủ PRD v2. | Cập nhật TDD bám sát PRD v2, bổ sung worker riêng cho việc nén ZIP. |
| **Scalability** | **Nút thắt cổ chai Băng Thông (Bandwidth Egress):** Khi x100 traffic, chi phí băng thông trả ra từ Server (Egress) sẽ là khổng lồ nếu stream trực tiếp qua Nginx/FastAPI. | High | Tăng đột biến chi phí hạ tầng, băng thông nghẽn làm tốc độ tải rớt thảm hại. | Dịch chuyển luồng tải: API -> Redirect (HTTP 302) -> Trực tiếp file trên Cloudflare R2 / AWS S3. Bỏ việc tải trung gian qua Backend VPS. |

---

## 3. Top 10 Rủi Ro Lớn Nhất (Top 10 Risks)

1. **Delivery Architecture Gap:** Mất kết nối luồng dữ liệu giữa Celery (Worker) và FastAPI (API).
2. **SSRF Vulnerability:** Nguy cơ bị chiếm server qua URL payload độc hại do dùng Regex cản lọc IP.
3. **Event Loop Blocking:** `yt-dlp` kéo sập hiệu năng FastAPI vì chạy đồng bộ (sync).
4. **Local File System Trap (`/tmp`):** Trói buộc toàn bộ hệ thống vào 1 máy chủ vật lý.
5. **SQLite Concurrency Deadlock:** Không thể xử lý đồng thời nhiều Job update trạng thái.
6. **FFmpeg OOM Risk:** Tràn RAM server khi xử lý video dung lượng lớn / dài.
7. **Cleanup Race Condition:** Cronjob xóa nhầm file đang xử lý.
8. **Egress Bandwidth Cost:** Chi phí mạng tăng theo cấp số nhân do stream trực tiếp qua máy chủ VPS thay vì Object Storage.
9. **Missing Single Download Flow:** Thiết kế API không thân thiện với use-case phổ biến nhất.
10. **Orphan Jobs:** Không có cơ chế Graceful Shutdown, khi Restart Server các job đang chạy bị treo vĩnh viễn trong DB.

---

## 4. Các Phần Còn Thiếu Cần Bổ Sung (Missing Components)

1. **Sequence Diagram chi tiết cho luồng Tải & Gộp (Download & Merge):** Rõ ràng từng bước: Request -> Queue -> Processing -> Notify (SSE/Websocket) -> Stream -> Cleanup.
2. **Thiết kế SSE (Server-Sent Events) Payload & Reconnection Strategy:** Data format gửi progress như thế nào? Xử lý ra sao khi user rớt mạng lúc đang đợi?
3. **Data Model chi tiết cho Redis:** Định dạng Key-Value cho Rate limit, Pub/Sub channel cho Job.
4. **Cơ chế đóng gói ZIP:** Luồng xử lý cho Batch Download (chờ tải xong -> nén ZIP -> stream file ZIP).
5. **Thiết kế Hạ Tầng Đám Mây (Deployment Architecture):** Diagram biểu diễn VPC, Redis, API, Worker, Storage.

---

## 5. Câu Hỏi Cần Làm Rõ Với Tác Giả (Clarifications)

1. Tại sao lại cố chấp dùng SQLite khi đã có Redis (vốn có thể lưu Job State cực tốt và nhanh) hoặc PostgreSQL (chuẩn cho môi trường prod)?
2. Cơ chế nào để FastAPI biết Celery đã chạy lệnh FFmpeg xong để bắt đầu trả StreamingResponse về cho user?
3. Với mục tiêu "tải file 1080p+", dung lượng file tạm có thể lên tới 2-3GB/file. Tại sao lại lập lịch xóa 30 phút/lần thay vì xóa ngay khi client tải xong?
4. Đội ngũ có dự trù chi phí băng thông Egress chưa? VPS thông thường chỉ cho 1-2TB băng thông/tháng, 50 user tải tích cực có thể thổi bay giới hạn này trong 3 ngày.

---

## 6. Alternative Design Đáng Cân Nhắc

**Event-Driven + Object Storage (S3/MinIO) Approach:**
Thay vì Stream trực tiếp qua Backend, hãy để Backend làm nhiệm vụ "Orchestrator":
1. Nhận URL -> Push Job.
2. Worker nhận Job -> Tải -> Ném lên S3 (hoặc Cloudflare R2 miễn phí Egress).
3. Worker báo xong qua Redis Pub/Sub.
4. API Server đẩy Presigned URL (chỉ sống 15 phút) qua SSE cho Client.
5. Client tự tải thẳng từ S3/R2 bằng Presigned URL.
*(Lợi ích: Zero Egress Cost cho VPS Backend, Scale ngang vô hạn, FastAPI không bao giờ bị nghẽn mạng).*

---

## 7. Trade-offs Của Giải Pháp Hiện Tại

* **Dùng chung 1 VPS cho API và Worker:**
  * *Được:* Dễ deploy, chi phí ban đầu cực rẻ.
  * *Mất:* Không thể chịu lỗi (Single Point of Failure), hiệu năng API sẽ bị giật lag nếu FFmpeg ăn hết CPU/RAM.
* **Stream trực tiếp file từ Server (StreamingResponse):**
  * *Được:* Che giấu hoàn toàn nguồn gốc file, không lưu trữ lâu dài.
  * *Mất:* Máy chủ chịu tải 100% băng thông mạng. Client mạng yếu tải chậm sẽ chiếm dụng process/RAM của server lâu hơn.

---

## 8. Production Readiness Assessment & Scoring

* **Requirement Coverage Score:** 7.5 / 10 *(Thiếu ZIP, SEO, UI badges)*
* **Architecture Score:** 4.0 / 10 *(Gãy luồng nối giữa Worker và API)*
* **Scalability Score:** 3.0 / 10 *(Local `/tmp` và SQLite bóp chết khả năng scale)*
* **Reliability Score:** 4.0 / 10 *(Rủi ro OOM, DB Locked, Cronjob xóa nhầm)*
* **Security Score:** 5.0 / 10 *(SSRF phòng thủ lỏng lẻo)*
* **Maintainability Score:** 6.0 / 10
* **Production Readiness Score:** **4.5 / 10**

---

## 9. Conclusion

🚫 **REJECT AND REDESIGN**

**Lý do từ chối:**
Tài liệu vấp phải những lỗi sơ đẳng của thiết kế hệ thống phân tán (Distributed System): Không tính đến cách truyền file giữa các node bất đồng bộ, sử dụng cơ sở dữ liệu không an toàn cho môi trường đa luồng (SQLite + Celery), và chặn đứng việc mở rộng hệ thống (Local Storage coupling).

**Action Items (Next Steps):**
Tác giả tài liệu cần thay đổi kiến trúc (Architectural Pivot) ở 3 điểm cốt lõi trước khi submit lại:
1. Chốt phương án Delivery: S3 Presigned URL (Khuyến nghị) HOẶC Shared Volume + SSE notify.
2. Vứt bỏ SQLite, chuyển sang PostgreSQL (hoặc dùng full Redis cho state).
3. Sửa lỗ hổng bảo mật SSRF bằng cơ chế DNS Resolution Filter.
4. Bọc các hàm `yt-dlp` bằng thread/async.
