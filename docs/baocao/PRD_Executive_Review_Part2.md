# 📋 Executive PRD Review — Part 2

## 6. GROWTH & SEO STRATEGY REVIEW

### 6.1. SEO Potential — Rất cao nhưng PRD không đề cập

Video downloader là niche có search volume cực lớn:
- "youtube video downloader" — ~5M searches/tháng globally
- "tiktok downloader no watermark" — ~2M searches/tháng
- "facebook video downloader" — ~1M searches/tháng
- "instagram reels download" — ~500K searches/tháng

| Mức độ | Vấn đề |
|--------|--------|
| 🔴 Critical | PRD không có SEO strategy. Đây là kênh acquisition #1 cho loại sản phẩm này — bỏ qua = mất 90%+ traffic tiềm năng. |

### 6.2. Đề xuất SEO Architecture

**Landing Page Per Platform Strategy:**
```
taimoithu.com/                          → Main (target: "tải video online")
taimoithu.com/youtube-downloader        → YouTube (target: "tải video youtube")
taimoithu.com/tiktok-downloader         → TikTok (target: "tải video tiktok không logo")
taimoithu.com/facebook-downloader       → Facebook
taimoithu.com/instagram-downloader      → Instagram
taimoithu.com/twitter-downloader        → Twitter/X
```

Mỗi landing page cần:
- H1 chứa target keyword
- FAQ section (Schema markup FAQPage)
- "How to use" steps (Schema HowTo)
- SoftwareApplication schema markup
- Platform-specific features highlighted
- Internal linking giữa các pages

### 6.3. Competitive Moat Strategy

| Strategy | Feasibility | Impact |
|----------|------------|--------|
| **UI/UX premium** (no ads, fast, beautiful) | ✅ High | Differentiation mạnh — hầu hết competitors đầy ads |
| **Platform-specific landing pages** | ✅ High | SEO long-tail capture |
| **Batch download** | ✅ High | Ít competitors có feature này |
| **Speed benchmark** | 🟠 Medium | Khó prove objectively |
| **PWA / Browser extension** | 🟠 Medium | Mở rộng distribution channels |

### 6.4. Content Strategy

| Content Type | Purpose | Priority |
|-------------|---------|----------|
| Landing pages per platform | SEO capture | 🔴 Critical |
| FAQ page | Long-tail keywords + user support | 🟡 High |
| Blog: "How to download from X" | Organic traffic | 🟠 Medium |
| Changelog / Status page | Trust building | 🟠 Medium |

---

## 7. SECURITY & ABUSE PREVENTION REVIEW

### 7.1. Threat Model

| Threat | Severity | Attack Vector | Impact |
|--------|----------|--------------|--------|
| **SSRF** | 🔴 Critical | User submits internal URL (localhost, 169.254.x.x, cloud metadata 169.254.169.254) | Server compromise, cloud credentials leak |
| **Bot/Scraping Abuse** | 🔴 Critical | Automated scripts mass-download qua API | Bandwidth explosion, IP blocked by platforms |
| **Bandwidth Abuse** | 🟡 High | Single user tải hàng trăm video 4K/ngày | Server cost spike |
| **DDoS** | 🟡 High | Flood API endpoints | Service downtime |
| **Proxy Abuse** | 🟡 High | Users dùng service như proxy để bypass geo-restrictions | Legal liability |
| **Malicious URL Injection** | 🟠 Medium | XSS via crafted URL in metadata display | User session compromise |
| **Content Policy** | 🟠 Medium | Users tải adult/illegal content qua service | Hosting provider ban |

### 7.2. Đề xuất Mitigation

| Measure | Implementation | Priority |
|---------|---------------|----------|
| **URL Validation & Sanitization** | Whitelist allowed domains, block private IPs, validate URL format | 🔴 Critical |
| **Rate Limiting** | 10 requests/phút (anonymous), 30/phút (authenticated) | 🔴 Critical |
| **Download Quota** | Free: 10 downloads/ngày per IP. Premium: 100/ngày | 🟡 High |
| **CAPTCHA** | hCaptcha/Turnstile sau 5 downloads liên tiếp | 🟡 High |
| **Bandwidth Quota** | Max 2GB/ngày per IP (free tier) | 🟡 High |
| **WAF** | Cloudflare Free tier — bot protection, DDoS mitigation | 🟡 High |
| **Device Fingerprinting** | FingerprintJS để detect multi-account abuse | 🟠 Medium |
| **Max File Size** | Từ chối tải video > 2GB (configurable) | 🟠 Medium |
| **Request Signing** | HMAC-signed API requests từ frontend — prevent direct API abuse | 🟠 Medium |
| **Metadata Sanitization** | HTML-escape tất cả video title/description trước khi render | 🟠 Medium |

---

## 8. OPERATIONS REVIEW

### 8.1. Operational Readiness Gaps

| Area | Status | Gap |
|------|--------|-----|
| **Monitoring** | ❌ | Không có application monitoring, error tracking, performance metrics |
| **Alerting** | ❌ | Không có alert khi platform extractor break, server overload, error spike |
| **Incident Response** | ❌ | Không có runbook, escalation path, rollback procedure |
| **On-Call** | ❌ | Solo project → single point of failure cho operations |
| **Customer Support** | ❌ | Không có FAQ, contact form, error guidance |
| **Release Management** | ❌ | Không có versioning strategy, rollback plan, canary deployment |

### 8.2. yt-dlp Update Strategy — Critical

| Mức độ | Vấn đề |
|--------|--------|
| 🔴 Critical | yt-dlp release ~1-2 lần/tuần. YouTube thay đổi → yt-dlp phải update → service phải redeploy. Không có auto-update strategy = service break thường xuyên. |

**Đề xuất yt-dlp Update Pipeline:**
```
1. Cron job check yt-dlp releases mỗi 6h
2. Auto-pull latest version vào staging
3. Run automated smoke tests (5 URLs × 5 platforms)
4. Nếu pass → auto-deploy to production
5. Nếu fail → alert maintainer, keep current version
```

### 8.3. Platform Health Check

**Đề xuất automated health monitor:**
```
Mỗi 30 phút, test 1 URL cố định cho mỗi supported platform:
- YouTube: https://youtube.com/watch?v=[test_id]
- TikTok: https://tiktok.com/@[test_user]/video/[test_id]
- Facebook: https://facebook.com/watch/?v=[test_id]
- ... (mỗi platform 1 URL)

→ Log success/fail, response time
→ Alert nếu platform fail > 3 lần liên tiếp
→ Hiển thị platform status trên UI (green/yellow/red badge)
```

### 8.4. Ownership Matrix

| Area | Owner | Status |
|------|-------|--------|
| PRD & Product decisions | PM | ❌ Chưa define |
| Frontend development | FE Dev | ❌ Chưa define |
| Backend + yt-dlp integration | BE Dev | ❌ Chưa define |
| Infrastructure + DevOps | DevOps | ❌ Chưa define |
| Legal compliance | Legal/PM | ❌ Chưa define |
| SEO & Growth | Marketing/PM | ❌ Chưa define |

---

## 9. RISKS & ASSUMPTIONS

### 9.1. Validated Assumptions (từ review trước, vẫn đúng)
| # | Assumption | Risk Level | Evidence |
|---|-----------|------------|----------|
| 1 | yt-dlp hỗ trợ Tier 1 platforms (YT, TT, FB, IG, X) | ✅ Low | Confirmed — active extractors |
| 2 | Client-side download khả thi cho nhiều platforms | ❌ **False** | CORS + signed URLs + short expiry đã block hầu hết. ~80%+ phải server-side |
| 3 | YouTube DRM không ảnh hưởng đáng kể | ⚠️ **Uncertain** | DRM A/B testing ongoing, có thể expand |
| 4 | VTV Go, Zing MP3 được yt-dlp support | ❌ **False** | Không có extractors hoặc rất unstable |

### 9.2. New Risks Identified

| # | Risk | Probability | Impact | Mitigation |
|---|------|------------|--------|------------|
| 1 | YouTube expand DRM → 1080p+ không tải được | Medium | 🔴 Critical | Multi-client fallback, communicate limitation |
| 2 | Hosting provider ban vì copyright complaints | Medium | 🔴 Critical | Choose permissive provider, implement DMCA takedown process |
| 3 | IP bị rate-limit/block bởi platforms khi scale | High | 🟡 High | Rotating proxies (cost ↑), respect rate limits |
| 4 | yt-dlp project bị abandoned/legal action | Low | 🔴 Critical | Monitor project health, prepare fallback extractors |

---

## 10. BLOCKERS

| # | Blocker | Owner | Severity | Est. Time |
|---|---------|-------|----------|-----------|
| 1 | ⚖️ Legal review copyright/ToS | PM + Legal | 🔴 | 1 tuần |
| 2 | 💰 Business model / monetization | PM | 🔴 | 2-3 ngày |
| 3 | 🏗️ Tech stack final decision | Eng Lead | 🔴 | 1 ngày |
| 4 | 📋 API contracts + data model | Eng Lead | 🔴 | 3-5 ngày |
| 5 | 🎯 Success metrics & KPIs | PM | 🟡 | 1-2 ngày |
| 6 | 🔒 Security threat model | Eng Lead | 🟡 | 2-3 ngày |
| 7 | 📱 V1 scope (Tier 1 only) confirmation | PM | 🟡 | 1 ngày |

---

## 11. PRIORITIZED ACTION PLAN

### Phase 0: Pre-Development (2-3 tuần)
| # | Action | Owner | Priority | Deliverable |
|---|--------|-------|----------|-------------|
| 1 | Legal review | PM | 🔴 | Go/No-Go decision document |
| 2 | Chốt scope V1 = Tier 1 only (5 platforms) | PM | 🔴 | Updated PRD scope section |
| 3 | Chốt tech stack (React + FastAPI + Redis + Celery) | Eng Lead | 🔴 | Architecture Decision Record |
| 4 | Define business model | PM | 🔴 | Monetization plan |
| 5 | Write API contracts (OpenAPI spec) | BE Dev | 🔴 | api-spec.yaml |
| 6 | Security threat model + mitigation plan | Eng Lead | 🟡 | Security doc |
| 7 | Define success metrics | PM | 🟡 | Metrics framework doc |
| 8 | Create user flow diagrams | Designer | 🟡 | Figma/diagrams |
| 9 | Create dark mode design token mapping | Designer | 🟡 | Updated DESIGN.md |
| 10 | SEO architecture plan | PM | 🟠 | SEO strategy doc |

### Phase 1: V1 Development (6-8 tuần)
- Sprint 1-2: Backend API + yt-dlp integration (YouTube + TikTok)
- Sprint 3-4: Frontend UI + single download flow
- Sprint 5-6: Batch download + remaining Tier 1 platforms
- Sprint 7-8: Security hardening + testing + SEO pages

### Phase 2: V2 Growth (4 tuần)
- Tier 2 platforms
- Analytics + measurement
- Performance optimization
- PWA support

---

## 12. FINAL SCORECARD

| Tiêu chí | Điểm | Trend vs Review trước | Ghi chú |
|----------|-------|----------------------|---------|
| Problem Statement & Vision | 2/10 | = | Vẫn thiếu problem definition |
| Product Strategy & Positioning | 2/10 | **NEW** | Không có competitive analysis, USP, monetization |
| User Research & Personas | 2/10 | = | Không có data |
| Functional Requirements | 5/10 | = | Features rõ, thiếu edge cases |
| Non-Functional Requirements | 1/10 | = | Gần như không có |
| UX/UI Specification | 5/10 | = | Visual tốt, thiếu flows/states |
| Technical Architecture | 3/10 | = | Chưa quyết định, thiếu API spec |
| Scalability & Cost Planning | 1/10 | **NEW** | Không có capacity planning hay cost projection |
| Security & Abuse Prevention | 0/10 | = | Hoàn toàn thiếu |
| Growth & SEO Strategy | 0/10 | **NEW** | Hoàn toàn thiếu — miss lớn cho product loại này |
| Operations & Maintenance | 0/10 | **NEW** | Không có monitoring, update strategy, support plan |
| Metrics & Measurement | 0/10 | = | Hoàn toàn thiếu |
| Timeline & Milestones | 2/10 | = | Quá chung |
| **TỔNG READINESS** | **3.5/10** | = | **Chưa sẵn sàng phát triển** |

---

## 13. QUESTIONS FOR PRD AUTHOR

### 🔴 Critical (Must answer before any development)
1. Đã có ý kiến pháp lý về copyright/ToS violations chưa?
2. Business model là gì? Ai chịu chi phí server?
3. Có đồng ý thu hẹp V1 scope xuống chỉ 5 Tier 1 platforms?
4. Có đồng ý tech stack: React + FastAPI + Redis?

### 🟡 High (Must answer before sprint planning)
5. Có user accounts hay anonymous-only?
6. Download history persist ở đâu?
7. Giới hạn: max file size, max batch, max downloads/ngày?
8. Dark mode only hay có light mode toggle?
9. Target market: Việt Nam only hay global?

### 🟠 Medium (Answer during development)
10. SEO: có budget cho domain, hosting riêng?
11. Analytics tool preference?
12. Có budget cho rotating proxies khi scale?
13. Support channels: email, chat, FAQ only?

---

> **Kết luận cuối cùng:** PRD hiện tại là một **vision document tốt** với technical direction đúng. Tuy nhiên, cần 2-3 tuần bổ sung để trở thành **implementation-ready spec**. Ưu tiên #1 là Legal Review — nếu legal cho No-Go thì toàn bộ cần pivot sang approach khác (ví dụ: chỉ support platforms cho phép download, hoặc chuyển sang browser extension model).
