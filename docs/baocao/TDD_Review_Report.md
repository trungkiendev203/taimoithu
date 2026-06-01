# 🔬 Technical Design Review — "Tải Mọi Thứ" TDD v1.0

**Review Panel:** Principal Architect · Staff Engineer · Sr. Backend/Frontend · DevOps · Security · EM  
**Document Under Review:** [01_Technical_Design_Document.md](file:///E:/taimoithu/docs/01_Technical_Design_Document.md)  
**Date:** 2026-05-30 | **Verdict:** `REVISION REQUIRED`

---

## EXECUTIVE SUMMARY

*   **Readiness Score:** **6.0 / 10**
*   **Overall Recommendation:** Nền tảng kiến trúc đi đúng hướng, nhưng còn nhiều lỗ hổng thiết kế chi tiết cần bổ sung trước khi implementation.
*   **Go / Conditional Go / No-Go:** **REVISION REQUIRED** (Yêu cầu chỉnh sửa bắt buộc trước khi phê duyệt bắt đầu Sprint 1).

**So sánh với PRD v2:** TDD align tốt với PRD về scope (Tier 1, 5 platforms) và tech stack (React, FastAPI, Redis, Celery). Tuy nhiên TDD thiếu một số yêu cầu PRD đã định nghĩa: ZIP packaging cho batch, iOS Safari guidance popup, SEO landing pages routing, và platform health badge trên UI.

---

## STRENGTHS

*   **S1. Kiến trúc tổng thể đi đúng hướng:** Mô hình "Micro-Monolith bất đồng bộ" — FastAPI stateless + Celery workers — là lựa chọn phù hợp cho V1. Phân tách rõ API layer (nhẹ, nhanh) và Job Processing layer (nặng, tốn thời gian) là quyết định kiến trúc tốt.
*   **S2. Queue splitting thông minh:** Phân chia "Queue Nhanh" (Direct Stream) và "Queue Chậm" (FFmpeg) thể hiện hiểu biết sâu về workload characteristics. Tránh được tình trạng FFmpeg job block direct stream job.
*   **S3. Job state machine rõ ràng:** State diagram `PENDING → PROCESSING → STREAMING/MERGING → COMPLETED/FAILED` với retry logic (Max 3) là thiết kế production-ready. Có timeout strategy (5min soft/10min hard).
*   **S4. Security baseline đầy đủ cho V1:** SSRF prevention, rate limiting, file size limit (2GB), Nginx bandwidth throttling, Cloudflare WAF — đây là bộ controls đủ tốt cho V1.
*   **S5. Failure scenarios được document đầy đủ:** Bảng failure scenarios (Section 12) cover được các case phổ biến nhất: URL sai, video private, hết đĩa, user disconnect, batch partial failure. Có cả UX message cho mỗi case.
*   **S6. Zero-disk-footprint goal rõ ràng:** Mục tiêu không lưu file vĩnh viễn + cleanup service mỗi 5 phút là approach giảm thiểu rủi ro pháp lý và cost đúng đắn.
*   **S7. PRD-to-Technical mapping:** Bảng mapping PRD ID → Technical Requirement (Section 2.1) đảm bảo traceability. Mỗi PRD feature đều có technical counterpart.

---

## CRITICAL GAPS

### 🔴 CG-1. Download Pipeline thiếu chi tiết end-to-end
*   **Vấn đề:** TDD mô tả 2 luồng riêng biệt nhưng không define rõ decision logic: luồng nào dùng Direct Stream, luồng nào dùng FFmpeg? Ai quyết định? Khi nào?
*   **Cụ thể thiếu:**
    *   Logic phân loại format: YouTube 1080p+ = cần merge (video-only + audio-only). YouTube 720p = direct stream (video+audio combined). TikTok = luôn direct. Facebook = luôn direct.
    *   Sequence diagram cho luồng Download (chỉ có cho Analyze).
    *   Cách stream file merged từ Celery worker về client qua FastAPI — Celery không native hỗ trợ streaming response.
*   **Tác động (Impact):** Engineer sẽ không biết implement download endpoint thế nào, đặc biệt luồng FFmpeg → stream back to client.
*   **Đề xuất:** Bổ sung sequence diagram cho cả 2 luồng download và decision tree phân loại format.

### 🔴 CG-2. Celery Worker → Client Streaming: Thiếu cơ chế truyền dữ liệu
*   **Vấn đề:** Đây là architectural gap lớn nhất. TDD viết: *"Worker dùng yt-dlp tải → FFmpeg merge → Stream file về client"* — nhưng **không giải thích cách nào Celery worker stream trực tiếp về client.** Celery là task queue async — worker chạy background, không giữ HTTP connection với client. Vậy sau khi merge xong, file merged sẽ:
    *   (A) Lưu tạm trên disk → FastAPI đọc file → StreamingResponse về client?
    *   (B) Celery ghi vào shared storage (Redis? NFS?) → FastAPI đọc từ đó?
    *   (C) Celery push notification qua SSE/WebSocket → client gọi API download riêng?
*   **Tác động (Impact):** Nếu không chốt, team sẽ implement sai hoặc phải refactor toàn bộ download flow.
*   **Đề xuất:** Khuyến nghị chọn approach **(C)**: Celery merge xong → lưu temp file → update job status = STREAMING → notify qua SSE → client gọi `GET /download/{job_id}/stream` → FastAPI stream file + delete sau khi stream xong.

### 🔴 CG-3. SSE/WebSocket cho progress — Chỉ mention, không design
*   **Vấn đề:** PRD mapping (Section 2.1) ghi *"SSE/WebSocket để push progress"* nhưng TDD không design:
    *   SSE hay WebSocket? (Khác nhau về connection management, scaling, proxy support).
    *   Progress data format? (percentage? bytes? speed?).
    *   Cách Celery worker report progress về FastAPI server?
    *   Reconnection strategy khi SSE bị ngắt?
    *   Scale: 50 concurrent SSE connections trên 1 FastAPI instance — có vấn đề gì?
*   **Tác động (Impact):** Frontend engineer không biết implement progress tracking. Backend engineer không biết report progress từ Celery worker thế nào.
*   **Đề xuất:** Chọn **SSE** (đơn giản hơn WebSocket, one-way đủ cho use case này). Celery worker → publish progress vào Redis Pub/Sub → FastAPI SSE endpoint subscribe → push tới client. Định nghĩa progress event format:
    ```json
    {"job_id": "xxx", "status": "PROCESSING", "progress": 45, "speed": "2.5MB/s", "eta": "12s"}
    ```

### 🔴 CG-4. API thiếu endpoint single download
*   **Vấn đề:** Section 6 định nghĩa 3 endpoints:
    1.  `POST /api/v1/analyze` — phân tích URL.
    2.  `POST /api/v1/download/batch` — tải hàng loạt.
    3.  `GET /api/v1/download/{job_id}/stream` — stream file.
*   **Thiếu:** Endpoint cho **single download**. User tải 1 video (use case phổ biến nhất) dùng API nào? Batch API với `urls: [1 url]`? Hay có endpoint riêng `POST /api/v1/download`?
*   **Tác động (Impact):** Frontend không biết gọi API nào cho use case chính.
*   **Đề xuất:** Thêm `POST /api/v1/download` cho single download. Hoặc document rõ rằng single download = batch với 1 URL.

### 🔴 CG-5. SSRF Prevention không đủ mạnh
*   **Vấn đề:** TDD ghi: *"dùng regex cấm các dải IP"*. Regex-based IP blocking là **không đủ** vì:
    *   URL có thể chứa hostname resolve ra IP nội bộ (DNS rebinding attack).
    *   URL redirect chain: `https://legit-site.com` → 302 → `http://169.254.169.254/metadata`.
    *   IPv6 loopback `::1`, IPv4-mapped IPv6 `::ffff:127.0.0.1`.
    *   URL encoding bypass: `http://0x7f000001` (hex encoding của 127.0.0.1).
*   **Tác động (Impact):** SSRF vẫn có thể xảy ra → cloud metadata leak → server compromise.
*   **Đề xuất:**
    1.  Resolve DNS trước → kiểm tra resolved IP (không phải URL string).
    2.  Block sau DNS resolution: private ranges, link-local, loopback, IPv6 equivalents.
    3.  Disable redirect following trong HTTP client, hoặc validate mỗi hop.
    4.  Chạy yt-dlp trong sandbox (Docker container riêng, network namespace restricted).

---

## HIGH PRIORITY IMPROVEMENTS

*   **🟡 HI-1. SQLite + Concurrent Celery Workers = Data corruption risk:** SQLite không hỗ trợ concurrent writes tốt. TDD đề cập WAL mode, nhưng nhiều Celery workers cùng UPDATE `DOWNLOAD_JOB.status` đồng thời → SQLite lock contention. WAL mode giúp nhưng không giải quyết hoàn toàn. Hơn nữa, Railway deployment = SQLite file trên ephemeral filesystem → **mất data khi redeploy**.
    *   *Đề xuất:* Dùng **Redis** cho job status tracking (đã có Redis cho queue) + SQLite chỉ cho IP quota (ít writes). Hoặc chuyển sang PostgreSQL từ V1 (Railway cung cấp managed PostgreSQL free tier).
*   **🟡 HI-2. Cache invalidation strategy thiếu:** TDD ghi *"Cache toàn bộ kết quả phân tích URL trong 1 giờ"*. Nhưng nếu video bị xóa trong 1h → cache trả metadata cũ → download fail. Cache key là gì? Full URL hay Normalized URL?
    *   *Đề xuất:* Cache key = normalized URL (extract video ID). TTL = 30 phút. Cache chỉ metadata, không cache format list (format availability thay đổi nhanh).
*   **🟡 HI-3. FFmpeg concurrency limit thiếu enforcement mechanism:** TDD ghi *"Giới hạn 2 concurrent jobs cho mỗi Worker FFmpeg"* nhưng không nói cách enforce.
    *   *Đề xuất:* Celery config: `--concurrency=2` cho FFmpeg queue. Hoặc dùng Celery semaphore/lock pattern. Document cụ thể config.
*   **🟡 HI-4. Không có graceful shutdown cho workers:** Khi deploy mới hoặc scale down, Celery worker đang xử lý FFmpeg job sẽ bị kill → file tạm bị mồ côi (orphan), job stuck ở PROCESSING.
    *   *Đề xuất:* Implement Celery `worker_shutting_down` signal → soft terminate current job → mark as PENDING for retry. Set `CELERY_WORKER_LOST` handler.
*   **🟡 HI-5. Cleanup service race condition:** Cronjob xóa file > 30 phút. Nhưng nếu FFmpeg đang merge file vào phút 29 → cronjob chạy phút 30 → xóa file input đang dùng.
    *   *Đề xuất:* Không dùng cronjob. Thay bằng: mỗi Celery task tự cleanup file tạm trong `finally` block. Cronjob chỉ là safety net cho orphan files, với age threshold = 60 phút thay vì 30.
*   **🟡 HI-6. Monitoring quá sơ sài:** Chỉ 3 metrics (`job_queue_length`, `ffmpeg_processing_time`, `yt_dlp_error_rate`). Thiếu nhiều metrics quan trọng.
    *   *Đề xuất bổ sung:* `download_success_rate` per platform, `active_sse_connections`, `temp_disk_usage_bytes`, `bandwidth_egress_bytes_total`, `api_response_time_p95`.

---

## ARCHITECTURE RISKS

*   **AR-1. Single Redis = Single Point of Failure:** Redis đang serve 3 roles: Rate Limiter + Message Broker + Cache. Nếu Redis down → toàn bộ hệ thống down. V1 acceptable, nhưng cần document Redis HA plan cho V2 (Redis Sentinel hoặc managed Redis).
*   **AR-2. FastAPI Blocking Risk từ yt-dlp:** `yt-dlp.extract_info()` là synchronous blocking call có thể mất 3-15s. Nếu chạy trực tiếp trong FastAPI async event loop sẽ block toàn bộ server.
    *   *Đề xuất:* Chạy yt-dlp trong `asyncio.to_thread()` hoặc dùng `run_in_executor()` để không block event loop.
*   **AR-3. Coupling giữa Platform Detection và yt-dlp:** TDD ghi: *"Regex router để gọi đúng yt-dlp extractor"*. Nhưng yt-dlp đã có built-in extractor matching. Tạo regex riêng = duy trì 2 bộ logic detect trùng nhau.
    *   *Đề xuất:* Chỉ dùng regex để validate URL format (hợp lệ, thuộc 5 platforms). Để yt-dlp tự chọn extractor. Không duplicate extractor routing logic.

---

## SCALABILITY RISKS

*   **SR-1. Vertical scaling wall cho FFmpeg:** FFmpeg là CPU-bound. 1 VPS 2 vCPU chỉ chạy được 2 concurrent merge. 50 users cùng tải YouTube 1080p = 50 FFmpeg jobs → queue depth = 48 → wait time > 10 phút.
    *   *Đề xuất:* Document capacity model. Phần lớn downloads sẽ là direct stream (TikTok, FB, IG, YT ≤720p). Estimate: ~20% YouTube 1080p+ = ~10 FFmpeg jobs.
*   **SR-2. SQLite không scale horizontally:** Nếu chạy 2+ FastAPI instances → 2 SQLite files độc lập → data inconsistency. Cần chuyển sang DB ngoài (PostgreSQL) sớm.
*   **SR-3. Bandwidth cost tại 1000+ DAU chưa được tính toán:** Ở 1000 DAU × 10 downloads × 300MB avg = 3TB/ngày egress. Phải có dự toán chi phí server/bandwidth của Railway để tránh hóa đơn tăng vọt.

---

## SECURITY RISKS

*   **SEC-1. yt-dlp chạy untrusted URL = Code execution risk:** yt-dlp xử lý đầu vào từ bên ngoài. Nếu có lỗ hổng trong extractor → có nguy cơ Remote Code Execution (RCE).
    *   *Đề xuất:* Chạy yt-dlp subprocess với `--no-exec`, `--no-post-overwrites` hoặc chạy trong sandbox Docker container bị giới hạn network.
*   **SEC-2. Metadata XSS:** Video title/description từ yt-dlp có thể chứa mã HTML/JS. Nếu frontend render trực tiếp → XSS.
    *   *Đề xuất:* Backend sanitize tất cả metadata string fields trước khi trả về API. Frontend luôn escape khi render.
*   **SEC-3. IP spoofing bypass rate limit:** Nếu đứng sau Cloudflare + Nginx, IP detection cần dùng `CF-Connecting-IP` header (trusted), tránh dùng `X-Forwarded-For` trực tiếp vì dễ bị bypass bằng spoofing.

---

## OPERATIONAL RISKS

*   **OPS-1. Không có runbook cho yt-dlp failure:** Khi YouTube thay đổi thuật toán → yt-dlp break → error rate spike. Cần có runbook auto-disable platform lỗi và hiển thị cảnh báo trên UI thay vì để hệ thống crash âm thầm.
*   **OPS-2. Railway ephemeral filesystem:** Mỗi lần deploy trên Railway là reset disk, mất SQLite file và các file tạm. Cần sử dụng Persistent Volume mount hoặc migrate SQLite sang Postgres.
*   **OPS-3. Thiếu alert pipeline:** Thiếu định nghĩa rules cảnh báo về Slack/Email khi error rate tăng đột biến hay ổ đĩa bị đầy.

---

## MISSING DECISIONS

| # | Quyết định kỹ thuật còn thiếu | Thời hạn cần chốt |
|---|-----------------------------|-------------------|
| 1 | **SSE vs WebSocket** cho progress tracking | Trước Sprint 1 |
| 2 | **Cơ chế deliver merged file** từ worker về client | Trước Sprint 1 |
| 3 | **Single download API endpoint** | Trước Sprint 1 |
| 4 | **URL normalization** (cache key strategy) | Trước Sprint 2 |
| 5 | **yt-dlp blocking handling** trong FastAPI async | Trước Sprint 1 |
| 6 | **Railway persistent storage** cho SQLite/temp | Trước deployment |
| 7 | **CORS configuration rules** | Sprint 1 |
| 8 | **Frontend state management** (Zustand? Context?) | Sprint 2 |
| 9 | **Celery result backend configuration** | Sprint 1 |

---

## MISSING COMPONENTS

| # | Module / Tài liệu thiếu | Có trong PRD v2? | Có trong TDD? | Mức độ ưu tiên |
|---|-------------------------|-----------------|--------------|---------------|
| 1 | Download sequence diagram (cả 2 flows) | N/A | ❌ | 🔴 Critical |
| 2 | SSE/Progress tracking detail design | ✅ | ❌ | 🔴 Critical |
| 3 | Single download API endpoint spec | Có ngụ ý | ❌ | 🔴 Critical |
| 4 | ZIP packaging cho batch download | ✅ PRD 3.2 | ❌ | 🟡 High |
| 5 | UX flow cho iOS Safari download | ✅ PRD 3.1 | ❌ (chỉ mention test) | 🟡 High |
| 6 | SEO landing pages routing design | ✅ PRD 7 | ❌ | 🟠 Medium |
| 7 | Platform health badge on UI | ✅ PRD 8 | ❌ (backend only) | 🟠 Medium |

---

## QUESTIONS REQUIRING CLARIFICATION

### Từ Product/Design:
1.  **Batch download xong → user tải từng file hay ZIP?** PRD v2 nói có ZIP. TDD không đề cập. ZIP = thêm processing time + disk space.
2.  **Progress tracking cho direct stream** — có cần progress bar không? (yt-dlp direct stream không biết total size trước).
3.  **"Premium" tier trong V1 hay V2?** PRD nói Freemium, TDD chỉ implement free tier (10 downloads/day/IP).

### Từ Engineering:
4.  **yt-dlp `extract_info()` trung bình mất bao lâu per platform?** Cần benchmark thực tế để validate SLA < 5s.
5.  **Railway free tier có bao nhiêu bandwidth?** TDD claim 1Gbps nhưng Railway free tier giới hạn egress.
6.  **SQLite trên Railway — persistent volume hay ephemeral?** Quyết định này ảnh hưởng toàn bộ data layer.

### Từ DevOps/Security:
7.  **Cloudflare Free tier có đủ cho Bot Fight Mode không?** Hay cần Pro ($20/mo)?
8.  **yt-dlp auto-update pipeline — rollback nếu new version có bug?** TDD chỉ có forward deployment.

---

## REQUIRED REVISIONS

### 🔴 Must-Fix (Bắt buộc trước Sprint 1)
*   **R1. Bổ sung download sequence diagram** cho cả 2 flows (direct + FFmpeg) vào Section 8.
*   **R2. Design cơ chế Celery → Client delivery** (recommend: temp file + SSE notify + stream endpoint) tại Section 4.6.
*   **R3. Thiết kế chi tiết SSE progress tracking** (Redis Pub/Sub + event formats).
*   **R4. Thêm `/api/v1/download` endpoint** cho single download vào Section 6.
*   **R5. Nâng cấp bảo mật SSRF:** validate IP sau DNS resolution, chặn redirect chain.

### 🟡 Should-Fix (Bắt buộc trước Sprint 2)
*   **R6. Chuyển đổi SQLite sang PostgreSQL** để tránh write lock và mất dữ liệu trên Railway ephemeral disk.
*   **R7. Implement `asyncio.to_thread`** hoặc executor cho yt-dlp calls trong FastAPI backend để tránh block server.
*   **R8. Thiết kế cấu trúc error response chuẩn hóa** (error code + message + retry_after).
*   **R9. Xây dựng capacity model** cho 50 CCU (ước tính hàng đợi FFmpeg).
*   **R10. Thiết kế ZIP packaging** cho batch download.

---

## FINAL RECOMMENDATION

### Verdict: `REVISION REQUIRED`

**Lý do:** TDD có **kiến trúc tổng thể đi đúng hướng** và **phạm vi V1 hợp lý**, nhưng có **5 Critical Gaps** (CG-1 đến CG-5) liên quan đến core logic (download pipeline, progress tracking, dynamic file streaming qua Celery và SSRF prevention) chưa được thiết kế đủ chi tiết. 

**Điều kiện chuyển sang Conditional Approval:**
1.  Giải quyết xong 5 Critical Gaps (CG-1 → CG-5).
2.  Bổ sung download sequence diagram cho cả 2 luồng tải.
3.  Chốt giải pháp lưu trữ dữ liệu (PostgreSQL thay vì SQLite trên ephemeral disk).

---

## COMPONENT-BY-COMPONENT SCORECARD

| Component | Score | Assessment |
|-----------|-------|-----------|
| **Overall Architecture** | 7/10 | Đúng hướng, phân tách rõ ràng. Thiếu deployment diagram. |
| **Frontend Architecture** | 4/10 | Quá sơ sài — chỉ 3 bullet points. Thiếu state mgmt, error boundary, SSE handling. |
| **Backend Architecture** | 7/10 | Solid. Thiếu async handling cho yt-dlp, thiếu single download endpoint. |
| **Database Design** | 5/10 | Schema hợp lý nhưng SQLite + Railway = vấn đề. Cần migration plan rõ hơn. |
| **Redis/Queue Design** | 7/10 | Queue splitting tốt. Thiếu Celery result backend config, consumer group design. |
| **Celery Worker Design** | 5/10 | Có concurrency limit nhưng thiếu delivery mechanism, graceful shutdown, progress reporting. |
| **Download Pipeline** | 3/10 | **Điểm yếu lớn nhất.** Thiếu sequence diagram, decision logic, delivery mechanism. |
| **yt-dlp Integration** | 6/10 | Biết dùng `extract_info()`, có User-Agent rotation. Thiếu async handling, sandboxing, error categorization. |
| **FFmpeg Pipeline** | 6/10 | Workflow rõ. Cleanup có risk race condition. Thiếu resource limit per process. |
| **Storage Strategy** | 7/10 | Zero-disk-footprint goal tốt. Cleanup service cần cải thiện để tránh race condition. |
| **Rate Limiting** | 7/10 | Redis-based, 10 req/min/IP. Thiếu IP detection strategy (CF header). |
| **Monitoring** | 4/10 | Quá sơ sài — 3 metrics, không alerting, không dashboards. |
| **Logging** | 6/10 | JSON format + IP hashing tốt. Thiếu retention policy, correlation ID. |
| **Error Handling** | 7/10 | Failure scenarios table tốt. Thiếu standardized error response format. |
| **Retry Strategy** | 7/10 | Max 3 retries, timeout defined. Thiếu backoff strategy. |
| **Security Controls** | 5/10 | Có baseline nhưng SSRF prevention yếu, thiếu XSS prevention, IP spoofing prevention. |
| **Cost Control** | 3/10 | Có bandwidth throttling nhưng không có cost projection, cost alerting. |
| **Scalability Strategy** | 5/10 | Stateless FastAPI tốt. FFmpeg bottleneck chưa model. SQLite chặn horizontal scale. |
| **Deployment Architecture** | 4/10 | Mention Railway+Vercel nhưng không diagram, không CI/CD, không rollback. |
| **Testing Strategy** | 7/10 | 4 layers (unit/integration/e2e/mobile). Thiếu load testing, security testing. |
| **PRD Alignment** | 6/10 | Tốt cho core features. Thiếu ZIP, iOS guidance, SEO routing, health badge UI. |
