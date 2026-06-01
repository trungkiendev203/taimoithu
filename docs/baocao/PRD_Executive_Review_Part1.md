# 📋 Executive PRD Review — "Tải Mọi Thứ"

**Review Level:** Staff PM · Principal Architect · Strategy Reviewer
**Date:** 2026-05-30 | **PRD Version:** v1.0 Draft

---

## EXECUTIVE SUMMARY

### Readiness Score: 3.5 → Cần nâng lên 7+ trước khi phát triển

### Top 5 Strengths
1. ✅ Vision rõ ràng: "one input, auto-detect, download" — UX flow đơn giản
2. ✅ Lựa chọn yt-dlp + FFmpeg là foundation kỹ thuật đúng đắn
3. ✅ Batch download với queue là differentiator so với competitors
4. ✅ Design system reference (Pinterest DS) tạo visual identity nhất quán
5. ✅ Component IDs tracking (`PRD-F01`, `PRD-SCR-MAIN`) cho traceability tốt

### Top 5 Risks
1. 🔴 **Legal:** Tải video vi phạm ToS hầu hết nền tảng — chưa có legal review
2. 🔴 **Scope Creep:** 20+ nền tảng + video + audio + playlist + livestream trong v1
3. 🔴 **Cost Explosion:** Bandwidth server-side proxy cho video 1080p+ không kiểm soát
4. 🔴 **Security:** URL input = SSRF vector, không có abuse prevention
5. 🟡 **Single Dependency:** yt-dlp là single point of failure cho toàn bộ service

### Go/No-Go Recommendation
> **NO-GO cho Development.** Cần 2-3 tuần bổ sung PRD trước khi sprint planning.

### Estimated Effort (sau khi PRD hoàn chỉnh)
- **V1 (Tier 1 — 5 nền tảng):** 6-8 tuần, 1 FE + 1 BE + 0.5 DevOps
- **V2 (Tier 2 mở rộng):** +4 tuần
- **V3 (Tier 3 + Growth):** +4 tuần

### Recommended Next Steps
1. Legal review → quyết định Go/No-Go thực sự
2. Chốt tech stack, scope V1 (chỉ Tier 1)
3. Viết API contracts + security threat model
4. Define success metrics + measurement plan
5. Tạo user flow diagrams + wireframes

---

## 1. PRODUCT STRATEGY REVIEW

### 1.1. Core Value Proposition — Chưa rõ ràng

PRD claim "tải mọi thứ" nhưng không xác định USP thực sự. Thị trường video downloader đã bão hòa (y2mate, savefrom, snaptik, cobalt.tools, 9xbuddy...).

| Mức độ | Vấn đề | Đề xuất |
|--------|--------|---------|
| 🔴 Critical | Không có competitive analysis, không xác định được differentiator | Phân tích 5 competitors chính, xác định 2-3 USP cụ thể |
| 🟡 High | Scope quá rộng — product identity mờ nhạt khi cố làm tất cả | Chọn 1 positioning rõ: "fastest" hoặc "highest quality" hoặc "best batch" |

**USP tiềm năng thực sự (đề xuất):**
1. **Batch download thông minh** — ít competitor làm tốt
2. **UI/UX premium** (dark mode, Pinterest-inspired) — hầu hết competitors UI rất xấu, đầy ads
3. **No ads, no popups** — nếu monetize khác (freemium)

### 1.2. Scope Feasibility & Scope Creep Risk

PRD đang cố đồng thời là: Video Downloader + Audio Downloader + Playlist Downloader + Social Media Saver + Livestream VOD Downloader + Image Downloader. Đây là **scope creep nghiêm trọng**.

| Mức độ | Phân tích |
|--------|-----------|
| 🔴 Critical | 20+ nền tảng trong v1 = phải test, maintain, monitor 20+ extractors. Mỗi khi 1 nền tảng thay đổi API → phải fix. Effort maintenance tỷ lệ thuận với số nền tảng. |

**Đề xuất Platform Tiering & Roadmap:**

#### Tier 1 — V1 Launch (Week 1-8)
| Nền tảng | yt-dlp Support | DRM Risk | Auth Required | Priority Rationale |
|----------|---------------|----------|---------------|-------------------|
| YouTube | ✅ Excellent | ⚠️ DRM A/B testing 2025+ | Cookies cho age-restricted | 70%+ search volume |
| TikTok | ✅ Good | ❌ None | ❌ | Top 2 demand globally |
| Facebook | ✅ Good | ❌ None | ❌ Public only | Top 3 social platform |
| Instagram | ⚠️ Unstable | ❌ None | ⚠️ Cookies needed for Stories | High demand nhưng extractor hay break |
| Twitter/X | ✅ Good | ❌ None | ⚠️ Cookies since 2023 | Stable extractor |

#### Tier 2 — V2 Expansion (Week 9-12)
| Nền tảng | yt-dlp Support | Risk | Rationale |
|----------|---------------|------|-----------|
| Reddit | ✅ Good, cần FFmpeg merge | Low | Niche nhưng stable |
| Pinterest | ✅ Good | Low | Align với design system |
| Vimeo | ✅ Excellent | Low | Professional content |
| Twitch Clips | ✅ Good | Low | Gaming audience |
| SoundCloud | ✅ Good | Low | Audio-first use case |

#### Tier 3 — V3 Regional (Week 13-16)
| Nền tảng | yt-dlp Support | Risk | Rationale |
|----------|---------------|------|-----------|
| Bilibili | ⚠️ Moderate | Medium, geo-restricted | Chinese market |
| Douyin | ⚠️ Unstable | High, changes frequently | Overlap với TikTok |
| Dailymotion | ✅ Good | Low | Low demand |
| Bandcamp | ✅ Good | Low | Niche audio |

#### ❌ Không khuyến nghị (Risk quá cao hoặc demand quá thấp)
| Nền tảng | Lý do loại |
|----------|-----------|
| IQIYI / Tencent Video | DRM protection, geo-blocked, legal risk cao |
| VTV Go | Không có yt-dlp extractor, phải custom scrape, legal risk VN |
| Zing MP3 / NCT | yt-dlp support rất yếu/không có, low global demand |
| Kuaishou | Unstable extractor, geo-restricted |
| Steam | Chỉ có trailer, extremely low demand |

### 1.3. Monetization Gap

| Mức độ | Vấn đề |
|--------|--------|
| 🔴 Critical | Không có business model. Server proxy video 1080p tốn ~$0.01-0.05/GB bandwidth. 1000 users/ngày × 500MB avg = $5-25/ngày = $150-750/tháng chỉ riêng bandwidth. |

**Đề xuất models:**
1. **Freemium:** Free 5 downloads/ngày, Premium unlimited ($3-5/tháng)
2. **Ad-supported:** Non-intrusive ads (không popup), free unlimited
3. **Hybrid:** Free với ads + Premium no-ads + batch download

---

## 2. FUNCTIONAL REVIEW

### 2.1. [PRD-F01] Auto-Platform Detection — Giữ nguyên đánh giá trước, bổ sung:

| Mức độ | Bổ sung | Đề xuất |
|--------|---------|---------|
| 🟡 High | YouTube DRM A/B testing 2025+ khiến một số format 1080p+ bị lock → user nhận được video thấp hơn expected | Implement fallback: thử multiple clients (web, android, ios), hiển thị warning cho user |
| 🟡 High | Instagram extractor break thường xuyên khi Meta thay đổi API | Implement health check per platform, hiển thị platform status badge |
| 🟠 Medium | Twitter/X yêu cầu cookies từ 2023 → không thể "just paste link" | Document limitation, hoặc implement cookie injection flow |

### 2.2. [PRD-F02] Quality Selection — Bổ sung:

| Mức độ | Bổ sung | Đề xuất |
|--------|---------|---------|
| 🟡 High | YouTube 1080p+ = separate video+audio streams → cần FFmpeg merge trên server → tốn CPU + bandwidth gấp đôi | Hiển thị rõ: "Requires server processing" vs "Direct download" |
| 🟠 Medium | Không đề cập subtitle/caption download | Bổ sung option tải phụ đề (SRT/VTT) — yt-dlp hỗ trợ sẵn |

### 2.3. [PRD-F03] Batch — Bổ sung:

| Mức độ | Bổ sung | Đề xuất |
|--------|---------|---------|
| 🔴 Critical | Batch download = force server-side cho tất cả → bandwidth cost × N | Giới hạn batch: Free 5 links, Premium 20 links |
| 🟡 High | Không có ZIP packaging cho batch result | Offer "Download as ZIP" option sau khi batch hoàn thành |
| 🟡 High | Không define queue persistence — refresh page = mất queue? | Persist queue state: localStorage (anonymous) hoặc DB (logged in) |

### 2.4. [PRD-F04] Speed — Bổ sung:

| Mức độ | Bổ sung | Đề xuất |
|--------|---------|---------|
| 🟡 High | "Client-Side Direct Download" claim sai cho hầu hết platforms trong 2026 — TikTok, Instagram, Facebook đều đã thêm signed URLs + short expiry + CORS headers | Honest assessment: 80%+ traffic sẽ server-side. Budget accordingly. |

---

## 3. NON-FUNCTIONAL REVIEW

*(Giữ nguyên từ review trước — tất cả vẫn thiếu: Performance SLAs, Security, Legal, Scalability, Privacy, Availability, i18n)*

---

## 4. UX REVIEW

### 4.1. User Flow — Cần tạo mới hoàn toàn

**Đề xuất Happy Path Flow:**
```
Landing → Paste URL → [Loading: Analyzing...] → Result Card (thumbnail, title, duration)
→ Select Quality → Click Download → [Progress Bar] → Complete → [Toast: Success]
```

**Error Paths cần define:**
```
Invalid URL → Error message + suggestion
Unsupported platform → "Platform not supported yet" + list supported
Private/deleted video → "Video unavailable" + reason
Rate limited by platform → "Please try again in X minutes"
Server error → "Something went wrong" + retry button
Network error → "Check your connection" + retry
```

### 4.2. Design System Conflict — Bổ sung chi tiết

| Mức độ | Conflict | Impact |
|--------|----------|--------|
| 🟡 High | DESIGN.md = Light Mode (canvas #ffffff, surface-card #f6f6f3). PRD = Dark Mode (#0B0F19, #121826). Đây là 2 hệ thống màu hoàn toàn khác nhau. | Phải tạo dark variant cho toàn bộ design tokens, không chỉ swap background. |
| 🟠 Medium | PRD text colors (#E2E8F0, #94A3B8) thuộc Tailwind slate palette, không phải Pinterest tokens | Tạo mapping table: Pinterest token → Dark mode equivalent |

### 4.3. Cross-Browser Download Experience

| Browser | File Size Limit | Resume Support | Issues |
|---------|----------------|---------------|--------|
| Chrome Desktop | ~2GB (Blob URL) | ❌ No (Blob) / ✅ Yes (direct) | Blob URLs không resume được |
| Firefox Desktop | ~2GB | Same | Same |
| Safari Desktop | ~2GB | ⚠️ Partial | Safari hay tự cancel large downloads |
| Edge Desktop | ~2GB | Same as Chrome | Same |
| **Android Chrome** | ~500MB practical | ❌ | Download manager riêng, UX khác |
| **iOS Safari** | ⚠️ **Severe limits** | ❌ | **Không hỗ trợ download file trực tiếp > vài trăm MB. Phải dùng Files app. Video không auto-save vào Photos.** |

| Mức độ | Vấn đề |
|--------|--------|
| 🟡 High | iOS Safari là pain point lớn nhất — download flow hoàn toàn khác desktop. PRD không đề cập. |
| 🟠 Medium | Large file downloads (>500MB, 4K video) sẽ fail trên mobile browsers. Cần warning cho user. |

---

## 5. TECHNICAL ARCHITECTURE REVIEW

### 5.1. Definitive Tech Stack Recommendation (V1)

**Không chấp nhận "A hoặc B".** Đề xuất cụ thể:

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Frontend** | **Vite + React** | Ecosystem lớn hơn Vue, `lucide-react` đã được chọn trong PRD, hiring pool rộng hơn |
| **Backend** | **Python FastAPI** | Native yt-dlp integration (Python lib), async support tốt, auto-docs OpenAPI |
| **Queue** | **Redis + Celery** | Proven stack cho Python, handle batch jobs + progress tracking |
| **Database** | **PostgreSQL** (nếu cần accounts) hoặc **SQLite** (V1 simple) | Structured data, migrations support |
| **Cache** | **Redis** | URL analysis cache (tránh re-analyze cùng URL), rate limiting |
| **Storage** | **No persistent storage** — stream piping only | Không lưu video trên server, giảm legal risk + storage cost |
| **Monitoring** | **Sentry (errors) + Uptime Robot (health)** | Free tier đủ cho V1 |
| **CI/CD** | **GitHub Actions** | Free cho public repo, đủ cho project scale này |
| **Hosting** | **Railway (backend) + Vercel (frontend)** | Đã có kinh nghiệm (từ conversation history), free tier khởi đầu |

### 5.2. Architecture: Queue, Worker, FFmpeg Pipeline

**Đề xuất kiến trúc:**
```
[Client Browser]
    │
    ├── POST /api/analyze {url} ──→ [FastAPI] ──→ [yt-dlp extract_info] ──→ Response {metadata, formats}
    │
    ├── GET /api/download?url=...&format=... ──→ [FastAPI] ──→ [yt-dlp stream pipe] ──→ Response Stream
    │                                                │
    │                                          (nếu cần merge)
    │                                                ↓
    │                                          [Celery Worker]
    │                                                │
    │                                          [FFmpeg merge]
    │                                                │
    │                                          [Stream result back]
    │
    └── POST /api/batch {urls[], format} ──→ [FastAPI] ──→ [Redis Queue] ──→ [Celery Workers ×3]
                                                                                    │
                                                                              [SSE/WebSocket progress]
```

**FFmpeg Pipeline concern:**

| Mức độ | Vấn đề | Impact |
|--------|--------|--------|
| 🔴 Critical | Mỗi FFmpeg merge operation: download video stream + audio stream + merge = 3× bandwidth + CPU | 1 video 1080p 10min ≈ 200MB video + 20MB audio + merge time ~30s |
| 🟡 High | FFmpeg processes nếu không limit sẽ eat toàn bộ server CPU/RAM | Max concurrent FFmpeg = 2-3 per server instance |

### 5.3. Scalability Analysis

| Scale | Users | Bandwidth/day | Server Needs | Monthly Cost Est. |
|-------|-------|--------------|-------------|-------------------|
| **Seed** | 100 DAU | ~50GB | 1 VPS (2 vCPU, 4GB RAM) | $20-40 |
| **Growth** | 1,000 DAU | ~500GB | 2-3 VPS + Load Balancer | $150-400 |
| **Scale** | 10,000 DAU | ~5TB | Auto-scaling cluster, CDN, dedicated workers | $1,500-5,000 |

| Mức độ | Vấn đề | Đề xuất |
|--------|--------|---------|
| 🔴 Critical | Ở 10K DAU, bandwidth cost ~$1.5-5K/tháng. Không có monetization = burn rate không bền vững. | **Phải có revenue model trước khi scale quá 1K DAU** |
| 🟡 High | FFmpeg workers là bottleneck chính — CPU-bound, không scale horizontally dễ | Separate FFmpeg workers onto dedicated compute instances |

### 5.4. Storage & CDN Strategy

| Mức độ | Đề xuất |
|--------|---------|
| 🟡 High | **Không lưu video trên server** — chỉ stream pipe. Lý do: (1) giảm legal risk, (2) giảm storage cost, (3) không cache copyrighted content |
| 🟠 Medium | **Cache URL analysis results** trong Redis (TTL 1h) — tránh re-analyze cùng URL nhiều lần |
| 🟠 Medium | **Static assets (FE)** serve qua Vercel CDN — zero cost, global edge |
