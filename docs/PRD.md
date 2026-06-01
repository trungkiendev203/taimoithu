# Tài Liệu Yêu Cầu Sản Phẩm (PRD) - Web Tải Video Đa Nền Tảng "Tải Mọi Thứ"

**Version:** 2.0 (Updated based on Executive Review)
**Readiness Score Target:** 8+/10 (Implementation-Ready)

Tài liệu này định nghĩa các yêu cầu sản phẩm, kiến trúc kỹ thuật, chiến lược bảo mật và vận hành cho ứng dụng web tải video tự động.

---

## 1. Tổng Quan Sản Phẩm (Product Overview)

- **Tên dự án:** Tải Mọi Thứ (All-in-One Video Downloader)
- **Unique Selling Propositions (USP):**
  1. **Batch download thông minh:** Tải hàng loạt video cùng lúc với hàng đợi rõ ràng.
  2. **UI/UX Premium:** Giao diện tối giản, tối màu (Dark mode), thiết kế chuẩn Pinterest, hoàn toàn không có quảng cáo popup (No intrusive ads).
- **Mô hình Kinh doanh (Monetization):**
  - **Freemium:** Miễn phí sử dụng cơ bản (Tối đa 10 lượt tải/ngày, giới hạn batch 5 link/lần).
  - **Premium:** Thu phí hàng tháng ($3-5/tháng) để mở khóa tải không giới hạn số lượng và tốc độ băng thông cao nhất.

---

## 2. Phạm Vi Ứng Dụng (Scope & Platform Tiering)

Để đảm bảo dự án khả thi và dễ bảo trì, lộ trình hỗ trợ nền tảng được chia thành các Tier. **Phiên bản V1 sẽ chỉ tập trung vào Tier 1.**

### 2.1. V1 Launch (Tier 1) - Priority Platforms
- **YouTube:** Hỗ trợ tải video, audio riêng biệt, cần xử lý FFmpeg cho độ phân giải 1080p+.
- **TikTok:** Tải video không hình mờ (No watermark) và audio.
- **Facebook:** Tải video từ Watch, Reels, bài viết công khai.
- **Instagram:** Tải Reels, Stories (cảnh báo: extractor có thể kém ổn định).
- **Twitter / X:** Tải video bài đăng.

### 2.2. V2 & V3 Expansion (Tier 2 & 3)
- Đẩy các nền tảng như Reddit, Pinterest, Twitch, SoundCloud, Douyin, Bilibili sang các phiên bản sau khi kiến trúc core đã ổn định.

---

## 3. Các Tính Năng Cốt Lõi & Trải Nghiệm Người Dùng (Features & UX)

### 3.1. Các Luồng Người Dùng Chính (User Flows)
**Happy Path:**
`Landing → Dán URL → [Loading/Analyzing] → Thẻ kết quả (Title, Duration, Thumbnail) → Chọn chất lượng → Click Download → [Progress Bar] → Hoàn thành → [Toast Success]`

**Error Paths:**
- *Invalid URL:* Báo lỗi định dạng và gợi ý cách lấy link đúng.
- *Rate Limited:* Báo lỗi "Vui lòng thử lại sau X phút".
- *Server Error:* Báo lỗi hệ thống và cung cấp nút "Thử lại".
- *Cross-browser Limitation:* Tự động phát hiện trình duyệt **iOS Safari** và hiện cảnh báo: *"Trình duyệt iOS hạn chế tải file lớn, file tải về sẽ nằm trong ứng dụng Tệp (Files), không tự động lưu vào Ảnh."*

### 3.2. Tính Năng Chức Năng (Functional Requirements)
- **Tự Động Nhận Diện Nền Tảng [PRD-F01]:** Hệ thống tự động phân tích URL để gửi cho yt-dlp extractor phù hợp. Có cơ chế Fallback (thử client web/android/ios) nếu YouTube áp dụng DRM mới.
- **Lựa Chọn Chất Lượng [PRD-F02]:** Phân tách rõ ràng luồng Direct Download và Server Processing (với những file cần gộp âm thanh/hình ảnh bằng FFmpeg). Cung cấp tùy chọn tải Audio (MP3 320kbps).
- **Tải Hàng Loạt Đồng Thời [PRD-F03]:** Sử dụng queue để xử lý song song tối đa 3 tiến trình cho người dùng Free. Có tính năng tải về dưới dạng tệp ZIP sau khi batch hoàn thành.

---

## 4. Kiến Trúc Kỹ Thuật (Technical Architecture)

Chốt stack công nghệ cho V1 để đảm bảo khả năng mở rộng (Scalability) và hiệu năng.

### 4.1. Tech Stack Quyết Định
- **Frontend:** **Vite + React** (Hệ sinh thái lớn, hỗ trợ tốt quản lý trạng thái tải).
- **Backend:** **Python FastAPI** (Tương thích native tốt nhất với `yt-dlp`, OpenAPI auto-docs).
- **Queue/Worker:** **Redis + Celery** (Xử lý hàng loạt và FFmpeg merging ngầm).
- **Database:** **SQLite** (cho V1, lưu trữ session/rate limit) hoặc **PostgreSQL** (nếu mở rộng hệ thống tài khoản).
- **Hosting:** **Vercel** (Frontend CDN) + **Railway/VPS** (Backend + Workers).

### 4.2. Kiến Trúc Luồng Xử Lý & FFmpeg Pipeline
- Client gọi API `/api/analyze`. FastAPI dùng yt-dlp (chỉ extract_info) đẩy về JSON metadata.
- Client gọi API tải. Backend đẩy job vào **Redis Queue**, **Celery Workers** nhận task tải và gộp (nếu cần FFmpeg).
- **Chiến lược Lưu trữ:** Không lưu file vĩnh viễn trên server (giảm rủi ro pháp lý và chi phí). File sau khi tải (hoặc stream-pipe trực tiếp) sẽ bị xóa ngay khi client tải xong.

---

## 5. Thiết Kế Giao Diện (UI/UX Concept)

Giao diện áp dụng hệ thống thiết kế **Pinterest Design System [DESIGN.md](file:///e:/taimoithu/.agents/skills/DESIGN.md)** phiên bản Sleek Dark Mode.

- **Thành phần giao diện & Ánh xạ ID:**
  - **[PRD-SCR-MAIN] Màn hình chính:** Tối giản, tập trung vào ô nhập liệu.
  - **[PRD-COMP-INPUT] Ô nhập liên kết:** Bo tròn viên thuốc (`rounded-full` 9999px), background tối (`#161D30`).
  - **[PRD-COMP-ANALYZE] Nút Phân Tích:** Nút gọi hành động màu Đỏ Pinterest đặc trưng (`#e60023`).
  - **[PRD-SCR-RESULT] Màn hình kết quả:** Thẻ thông tin **[PRD-COMP-METADATA]** và bộ chọn chất lượng **[PRD-COMP-QUALITY]** (bo góc 16px - `rounded-md`).
  - **[PRD-SCR-BATCH] Chế độ tải hàng loạt:** Hộp nhập nhiều link **[PRD-COMP-BATCH-INPUT]** và danh sách hàng đợi tải **[PRD-COMP-QUEUE]** kèm thanh tiến trình.

---

## 6. Bảo Mật & Chống Lạm Dụng (Security & Abuse Prevention) [PRD-SEC]

- **Phòng chống SSRF (Server-Side Request Forgery):** Validate nghiêm ngặt URL đầu vào, từ chối mọi yêu cầu trỏ vào dải IP nội bộ (`localhost`, `169.254.x.x`).
- **Rate Limiting:** Cấu hình giới hạn 10 requests/phút/IP để chống bot.
- **Quota & Bandwidth:** Giới hạn tải 10 file/ngày cho người dùng Free. Từ chối xử lý video nặng hơn 2GB để bảo vệ server RAM.
- **WAF:** Triển khai Cloudflare (Free tier) để chặn DDoS cơ bản.

---

## 7. Chiến Lược Tăng Trưởng & SEO (Growth & SEO) [PRD-SEO]

- **Cấu trúc Landing Page:** Xây dựng các trang đích tĩnh (Landing pages) theo từng nền tảng để thu hút Organic Traffic:
  - `/youtube-downloader` (Target keyword: tải video youtube)
  - `/tiktok-downloader` (Target keyword: tải video tiktok không logo)
- **Schema Markup:** Tích hợp `FAQPage` và `SoftwareApplication` schema cho các trang đích.

---

## 8. Vận Hành & Bảo Trì (Operations) [PRD-OPS]

- **Cập nhật yt-dlp tự động:** Thiết lập Cron Job chạy mỗi 12h. Tự động kiểm tra bản phát hành mới của yt-dlp, cài đặt vào môi trường staging, chạy test script (5 URL của 5 platform Tier 1). Nếu Pass, tự động promote lên Production.
- **Platform Health Monitoring:** Chạy script check trạng thái API nền tảng mỗi 30 phút. Hiển thị thông báo (Badge: Green/Red) trên UI Frontend nếu một nền tảng cụ thể đang bảo trì/thay đổi thuật toán.
- **Error Tracking:** Cài đặt Sentry để bắt exception từ FastAPI backend.

---

## 9. Kế Hoạch Triển Khai (Milestones)

- **Giai đoạn 1 (Tuần 1-2):** Thiết lập hạ tầng Backend (FastAPI, Redis, Celery), viết API phân tích YouTube & TikTok.
- **Giai đoạn 2 (Tuần 3-4):** Xây dựng Frontend (React + Vite + Tailwind/CSS Pinterest Design). Tích hợp API phân tích và luồng tải đơn.
- **Giai đoạn 3 (Tuần 5-6):** Hoàn thiện Batch Download, tích hợp FFmpeg worker, giới hạn Quota.
- **Giai đoạn 4 (Tuần 7-8):** Bổ sung Landing pages SEO, Audit Bảo mật, Testing toàn diện và Go-live V1.
