# Kế Hoạch Triển Khai Frontend MVP (Phase 4)

Dựa trên yêu cầu của bạn, Phase 4 sẽ thiết lập một ứng dụng Frontend hoàn chỉnh sử dụng **React + Vite** giao tiếp với các API Backend đã hoàn thiện từ Phase 1-3.

## 1. Công nghệ & Stack
- **Framework:** React 18 + Vite.
- **Styling:** Vanilla CSS (theo đúng guideline không dùng Tailwind trừ khi được yêu cầu rõ ràng, áp dụng UI/UX lấy cảm hứng từ Pinterest như bo góc mềm mại, đổ bóng shadow mượt mà, primary color đỏ đặc trưng `#E60023`). 
- Tích hợp một số nguyên tắc UI từ `misa/skills` (ví dụ: các ô input sạch sẽ, button hiển thị rõ ràng các trạng thái, notification toast).
- **Network:** `fetch` cho API calls, `EventSource` cho luồng SSE (tiến trình tải).

## 2. Cấu trúc thư mục (Dự kiến)
Thư mục `frontend/` sẽ được khởi tạo cùng cấp với `backend/` trong `e:\taimoithu\`:
```text
frontend/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── App.css
    ├── components/
    │   ├── UrlInput.jsx         # Form nhập URL
    │   ├── LoadingState.jsx     # Skeleton/Spinner khi Analyze
    │   ├── ResultCard.jsx       # Hiển thị thông tin Video & Chọn format
    │   ├── ProgressModal.jsx    # UI thanh Progress bar (cắm SSE)
    │   └── Toast.jsx            # Hiển thị thông báo mượt mà
    ├── services/
    │   └── api.js               # Các hàm fetch đến backend
    └── assets/
        └── css/
            └── variables.css    # Chứa màu sắc, font chữ chuẩn Pinterest
```

## 3. Lộ trình triển khai (Execution Steps)

1. **Khởi tạo Project:** Chạy `npx -y create-vite@latest frontend --template react` (tự động bỏ qua hỏi đáp).
2. **Cài đặt Styling (Vanilla CSS):** Tạo hệ thống biến màu sắc chuẩn Pinterest, thiết lập `index.css` global.
3. **Kết nối API (services/api.js):** 
   - Hàm `analyzeUrl(url)` gọi `GET /api/v1/analyze`.
   - Hàm `submitDownload(url, format_id)` gọi `POST /api/v1/download`.
   - Setup `EventSource` trỏ tới `GET /api/v1/download/{job_id}/events`.
4. **Xây dựng Components (UI):**
   - **Màn chính:** Ô text input to, bo tròn với nút "Analyze" đỏ rực.
   - **Màn kết quả:** Card bo góc hiển thị Thumbnail video, Title, Tác giả. Kèm theo một `<select>` drop-down để chọn Quality (VD: 1080p, 720p).
   - **Tiến trình tải:** Khi bấm nút "Download", bật một cửa sổ Modal hiển thị thanh Progress Bar chạy mượt mà, tốc độ mạng, thời gian còn lại (nhận data từ SSE). Nút "Tải xuống" xuất hiện khi đạt 100%.
5. **Cập nhật Docker Compose:** Viết `Dockerfile` cho frontend phục vụ qua Nginx hoặc expose Vite dev server. Chạy chung mạng với Backend.
6. **Tổng kết:** Tạo file `PHASE_4_SUMMARY.md`.

## Open Questions (Cần bạn duyệt)

1. Mình sẽ sử dụng Vanilla CSS hoàn toàn để tự do sáng tạo UI chuẩn Pinterest. Bạn đồng ý chứ?
2. Ứng dụng React này sẽ chạy ở port `5173`. Backend hiện tại chạy ở `8000`. Cấu hình CORS ở Phase 2 đã mở cổng `5173` rồi, nên sẽ chạy trơn tru. Mình sẽ tạo luôn một khối `frontend` vào `docker-compose.yml` để chạy song song nhé?

---
*Nếu bạn đồng ý với kế hoạch trên, hãy bảo mình "triển khai đi" để mình bắt đầu gõ lệnh tạo frontend!*
