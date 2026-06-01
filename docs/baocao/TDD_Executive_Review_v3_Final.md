# 🔬 Technical Design Review: "Tải Mọi Thứ" TDD v2.0 (Post-Revision)

**Reviewer Role:** Principal Engineer / Staff Software Engineer / Solution Architect
**Document:** 01_Technical_Design_Document.md (v2.0)
**Date:** 2026-05-30
**Objective:** Đánh giá lại tài liệu TDD sau đợt tái cấu trúc kiến trúc quy mô lớn để quyết định Go/No-Go cho Sprint 1.

---

## 1. Executive Summary

Bản cập nhật TDD v2.0 là một bước tiến vượt bậc so với phiên bản trước. Nhóm thiết kế đã thực hiện một cú "Architectural Pivot" cực kỳ chuẩn xác khi chuyển đổi từ kiến trúc "Micro-Monolith gắn liền Local Storage" sang **Kiến trúc Phân tán Hướng Sự kiện (Event-Driven Distributed Architecture) kết hợp Object Storage (Cloudflare R2/S3)**.

Các "tử huyệt" của phiên bản trước như gãy luồng tải (Delivery Gap), thắt cổ chai SQLite, lỗ hổng bảo mật SSRF bằng Regex, và nguy cơ quá tải băng thông Egress đều đã được giải quyết triệt để và thanh lịch. 

**Trạng thái hiện tại: Đã sẵn sàng cho quá trình Implementation.**

---

## 2. Những Cải Tiến Đột Phá (Key Architectural Wins)

* **🏆 Zero Egress Cost & Horizontal Scaling (Tuyệt vời):** Quyết định đẩy file từ Celery Worker thẳng lên Cloudflare R2 và stream về client qua Presigned URL là quyết định kiến trúc đáng giá nhất. FastAPI giờ đây trở nên siêu nhẹ (chỉ làm API Gateway và Orchestrator), tiết kiệm 90% chi phí băng thông, và Worker Node có thể scale vô hạn mà không sợ mất file tạm.
* **🏆 Luồng Dữ Liệu Rõ Ràng (SSE + Pub/Sub):** Thiết kế dùng Redis Pub/Sub để Worker báo cáo tiến độ và FastAPI mở kết nối SSE cho client là thiết kế kinh điển và chuẩn mực cho các bài toán xử lý nền dài hạn.
* **🏆 Bảo Mật SSRF Chuẩn Xác:** Chuyển từ chặn Regex sang chặn theo DNS Resolution ở cấp độ IP là cách duy nhất phòng thủ SSRF một cách triệt để trước các thủ thuật DNS Rebinding.
* **🏆 An Toàn Dữ Liệu (PostgreSQL & Cleanup):** Thay thế SQLite bằng PostgreSQL loại bỏ nguy cơ Deadlock khi Worker liên tục cập nhật trạng thái. Logic dọn dẹp file tạm chuyển về block `finally` của từng Task giúp loại trừ Race Condition.
* **🏆 Hoàn Thiện Trải Nghiệm (UX/SEO):** Đã bổ sung các tính năng cấp thiết từ PRD v2 như đóng gói file ZIP cho Batch, hiển thị cảnh báo cho iOS Safari và chiến lược SEO.

---

## 3. Một Số Điểm Cần Lưu Ý Khi Code (Implementation Recommendations)

Dù kiến trúc đã vững vàng, các kỹ sư cần lưu ý những rủi ro nhỏ sau trong quá trình lập trình thực tế (không cần thiết kế lại, chỉ cần chú ý khi viết code):

| Category | Điểm Lưu Ý Khi Code (Gotcha) | Đề xuất giải pháp |
| :--- | :--- | :--- |
| **API / Connection** | **Cạn kiệt Connection (Connection Exhaustion) vì SSE:** Nếu 1000 user giữ kết nối SSE cùng lúc, server FastAPI có thể bị hết socket hoặc worker, gây sập API. | Giới hạn timeout cho kết nối SSE (ví dụ: tối đa 30 phút). Sử dụng `uvicorn` với worker class `uvloop` để xử lý concurrency tốt nhất. |
| **External API** | **Định dạng `format_id: "best"` của yt-dlp:** Tham số `"best"` đôi khi chỉ trả về video chất lượng tối đa mà có sẵn âm thanh liền mạch (có thể chỉ là 720p). Nếu muốn gộp 1080p, cần cấu hình yt-dlp là `bestvideo+bestaudio/best`. | Đảm bảo code Backend xử lý linh hoạt tham số `format_id` tùy vào lựa chọn chất lượng của Client. |
| **Storage / Network** | **Lỗi Upload lên S3/R2:** Worker nén xong ZIP nhưng upload lên R2 thất bại do mạng chập chờn. | Sử dụng cơ chế Multipart Upload của thư viện `boto3` và cấu hình tự động retry (AWS SDK đã có sẵn, cần chắc chắn bật). |
| **Security** | **Presigned URL Leaking:** Nếu Presigned URL bị rò rỉ, người khác có thể tải và làm phát sinh chi phí R2 (dù rẻ). | Set thời gian sống (TTL - ExpiresIn) của Presigned URL xuống **tối đa 15 phút**. |
| **Cost Control** | **Quản lý rác trên Cloudflare R2:** File đã upload lên R2 để client tải, nếu client không tải thì file nằm đó vĩnh viễn và tốn tiền lưu trữ. | Cấu hình **Object Lifecycle Management** trên Cloudflare R2 bucket: Tự động xóa (Delete) tất cả object sau **24 giờ** kể từ lúc tạo. |

---

## 4. Production Readiness Assessment & Scoring

Thang điểm đã được nâng lên mức lý tưởng sau khi các lỗ hổng hệ thống được khắc phục.

* **Requirement Coverage Score:** 9.5 / 10 *(Đã bao phủ toàn bộ luồng PRD)*
* **Architecture Score:** 9.5 / 10 *(Luồng S3 + PubSub/SSE rất vững chắc)*
* **Scalability Score:** 9.0 / 10 *(Sẵn sàng scale 100x traffic ở cả Frontend, API và Worker)*
* **Reliability Score:** 8.5 / 10 *(Có cơ chế Graceful Shutdown và Timeout chuẩn)*
* **Security Score:** 8.5 / 10 *(DNS SSRF Prevention và WAF đã đủ mạnh)*
* **Maintainability Score:** 8.0 / 10 *(Phân tách layer rõ ràng, dễ bảo trì)*
* **Production Readiness Score:** **9.0 / 10**

---

## 5. Kết Luận Cuối Cùng

✅ **APPROVED FOR IMPLEMENTATION**

**Lời ngỏ từ Review Panel:**
Chúc mừng đội ngũ đã có một tài liệu TDD xuất sắc! Việc chuyển đổi mô hình lưu trữ và phân phối file là điểm sáng chói nhất của tài liệu này. 

Team có thể tự tin khởi động **Sprint 1** dựa trên TDD v2.0. Hãy lưu ý cấu hình thêm Rule tự xóa file rác (Lifecycle Rule) trên Cloudflare R2 để hệ thống chạy hoàn toàn "rảnh tay" (maintenance-free) về mặt hạ tầng nhé. Good luck!
