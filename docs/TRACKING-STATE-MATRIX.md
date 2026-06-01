# Ma Trận Theo Dõi Trạng Thái (Tracking State Matrix)

Bảng dưới đây ánh xạ các yêu cầu từ PRD với hệ thống thiết kế (Design System) và trạng thái triển khai thực tế. Bảng này giúp QA theo dõi tiến độ thi công.

## 1. Tính Năng Core & Trải Nghiệm Người Dùng
| PRD-ID | Tên Component / Feature | Loại | Ánh Xạ Design System | Trạng Thái Dev |
|--------|-------------------------|------|----------------------|----------------|
| **PRD-F01** | Tự Động Nhận Diện Nền Tảng | Flow | N/A | `[ ] Pending` |
| **PRD-F02** | Lựa Chọn Chất Lượng | Feature | N/A | `[ ] Pending` |
| **PRD-F03** | Tải Hàng Loạt Đồng Thời | Feature | N/A | `[ ] Pending` |
| **PRD-SCR-MAIN** | Màn Hình Chính | Screen | DS-SCR-MAIN | `[ ] Pending` |
| **PRD-COMP-INPUT**| Thanh Nhập Liên Kết | Component| DS-COMP-INPUT | `[ ] Pending` |
| **PRD-COMP-ANALYZE**| Nút Phân Tích | Component| DS-COMP-ANALYZE | `[ ] Pending` |
| **PRD-SCR-RESULT**| Màn Hình Kết Quả | Screen | DS-SCR-RESULT | `[ ] Pending` |
| **PRD-COMP-METADATA**| Thẻ Thông Tin Video | Component| DS-COMP-METADATA | `[ ] Pending` |
| **PRD-COMP-QUALITY**| Bộ Chọn Chất Lượng | Component| DS-COMP-QUALITY | `[ ] Pending` |
| **PRD-SCR-BATCH** | Chế Độ Tải Hàng Loạt | Screen | DS-SCR-BATCH | `[ ] Pending` |
| **PRD-COMP-BATCH-INPUT**| Hộp Nhập Nhiều Link| Component| DS-COMP-BATCH-INPUT| `[ ] Pending` |
| **PRD-COMP-QUEUE** | Danh Sách Hàng Đợi Tải| Component| DS-COMP-QUEUE | `[ ] Pending` |

## 2. Bảo Mật, SEO & Vận Hành (Non-Functional Requirements)
| PRD-ID | Tên Hạng Mục | Phụ Trách | Trạng Thái Dev | Ghi Chú |
|--------|--------------|-----------|----------------|---------|
| **PRD-SEC-01** | Chống SSRF (Validate URL) | Backend | `[ ] Pending` | Chặn IP nội bộ. |
| **PRD-SEC-02** | Rate Limiting & Quota | Backend | `[ ] Pending` | 10 req/min, 10 file/ngày (Free). |
| **PRD-SEO-01** | Landing Pages Theo Nền Tảng| Frontend | `[ ] Pending` | Tạo các URL động/static. |
| **PRD-SEO-02** | Schema Markup | Frontend | `[ ] Pending` | Cài đặt FAQPage, SoftwareApplication. |
| **PRD-OPS-01** | yt-dlp Auto-updater | DevOps/BE | `[ ] Pending` | Cronjob 12h check updates. |
| **PRD-OPS-02** | Platform Health Checks | DevOps/BE | `[ ] Pending` | Script check trạng thái extractor. |
