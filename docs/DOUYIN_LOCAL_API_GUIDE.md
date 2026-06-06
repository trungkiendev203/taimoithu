# Hướng dẫn Tích hợp và Tối ưu hóa API Douyin Nội bộ (Self-hosted)

Tài liệu này hướng dẫn cách chuyển đổi cơ chế tải video Douyin từ các dịch vụ bên thứ ba tốn phí (như Apify) sang sử dụng dịch vụ self-hosted **Douyin_TikTok_Download_API** nội bộ để tiết kiệm 100% chi phí vận hành và nâng cao tính chủ động của hệ thống **Tải Mọi Thứ**.

---

## 1. Lý do chuyển đổi
* **Tối ưu chi phí:** Các dịch vụ API bên thứ ba như Apify tính phí dựa trên số lượt quét, gây tốn kém lớn khi lượng người dùng tăng cao.
* **Tốc độ & Tính ổn định:** Dịch vụ self-hosted chạy trên môi trường cục bộ giúp giảm độ trễ mạng và không phụ thuộc vào hạn mức (rate limit) của bên thứ ba.
* **Khắc phục lỗi hết hạn Cookie:** Douyin thắt chặt bảo mật khiến cookie thường hết hạn sau 3-5 ngày. Dịch vụ nội bộ hỗ trợ endpoint cập nhật cookie động lập tức mà không cần khởi động lại ứng dụng.

---

## 2. Mô hình Tích hợp trong Hệ thống
Hệ thống **Tải Mọi Thứ** đã có sẵn tích hợp dịch vụ Evil0ctal thông qua module `evil0ctal_service.py`. Khi người dùng yêu cầu phân tích một link Douyin:
1. Hệ thống kiểm tra biến môi trường `APIFY_TOKEN`.
2. Nếu không có `APIFY_TOKEN`, luồng xử lý sẽ tự động chuyển sang gọi endpoint của **Douyin_TikTok_Download_API** nội bộ.
3. API nội bộ sẽ xử lý giải chữ ký `a_bogus` và sử dụng cookie hiện tại để lấy link video gốc chất lượng cao không watermark (NWM) và trả về cho client.

---

## 3. Các bước thiết lập Chi tiết

### Bước 1: Triển khai Douyin_TikTok_Download_API
Di chuyển vào thư mục dự án API:
```bash
cd E:\fashion-ecommerce\Douyin_TikTok_Download_API
```

Bạn có thể chạy dịch vụ này bằng hai cách:

#### Cách A: Chạy trực tiếp bằng Python (Khuyên dùng khi dev)
1. Cài đặt các gói phụ thuộc:
   ```bash
   pip install -r requirements.txt
   ```
2. Khởi chạy server:
   ```bash
   python start.py
   ```
   *Mặc định, server sẽ chạy tại địa chỉ `http://localhost:80` (Cổng 80).*

#### Cách B: Chạy bằng Docker
Khởi chạy container ở chế độ nền:
```bash
docker-compose up -d
```

---

### Bước 2: Cấu hình biến môi trường trên Tải Mọi Thứ
Để tắt hoàn toàn dịch vụ Apify và chuyển hướng toàn bộ yêu cầu Douyin sang dịch vụ nội bộ:

1. Mở file cấu hình biến môi trường `.env` của backend **Tải Mọi Thứ** (`E:\taimoithu\backend\.env`).
2. Sửa hoặc cấu hình các biến sau:
   ```env
   # Vô hiệu hóa Apify bằng cách xóa hoặc để trống Token
   APIFY_TOKEN=""

   # Chỉ định đường dẫn tới API Douyin nội bộ vừa khởi chạy
   EVIL0CTAL_URL="http://localhost:80"
   ```
3. Khởi động lại backend **Tải Mọi Thứ**. Dịch vụ sẽ ngay lập tức định tuyến các link Douyin qua API nội bộ.

---

## 4. Giải pháp Duy trì Cookie Hoạt động Liên tục (Maintenance-Free)

Điểm yếu lớn nhất của việc tự cào dữ liệu Douyin là Cookie thường bị hết hạn hoặc bị gắn cờ sau một thời gian ngắn. Để giải quyết vấn đề này mà không cần can thiệp thủ công vào file cấu hình:

### Cơ chế cập nhật Cookie động
Dịch vụ `Douyin_TikTok_Download_API` cung cấp một API cho phép cập nhật Cookie trực tiếp trong bộ nhớ và ghi đè vào file cấu hình `config.yaml` nội bộ mà không cần restart server:

* **Endpoint:** `POST /api/update_cookie` (Hoặc `/api/hybrid/update_cookie`)
* **Headers:** `Content-Type: application/json`
* **Request Body:**
  ```json
  {
    "service": "douyin",
    "cookie": "THAY_THẾ_BẰNG_CHUỖI_COOKIE_MỚI_LẤY_TỪ_TRÌNH_DUYỆT"
  }
  ```

### Gợi ý giải pháp tự động hóa lấy Cookie (Automation Sniffer)
Để hệ thống tự vận hành 24/7 mà không cần lập trình viên lấy cookie thủ công:
1. **Sử dụng Extension Trình duyệt:** Cài đặt Chrome extension Sniffer/Cookie Exporter hoặc viết một script Puppeteer/Playwright tự động đăng nhập vào trang chủ Douyin định kỳ mỗi 24 giờ trên một VPS sạch.
2. **Gửi API cập nhật:** Script tự động sau khi lấy được chuỗi cookie mới sẽ thực hiện gọi POST request gửi cookie đó tới endpoint `/api/update_cookie` của API nội bộ.
3. **Ví dụ bằng lệnh cURL gửi cập nhật:**
   ```bash
   curl -X POST "http://localhost:80/api/update_cookie" \
        -H "Content-Type: application/json" \
        -d '{"service": "douyin", "cookie": "__ac_nonce=...; ttwid=...; passport_csrf_token=...;"}'
   ```

---

## 5. Kiểm thử và Xác nhận
Sau khi cấu hình, bạn có thể thực hiện kiểm tra nhanh xem API nội bộ có trả về đúng dữ liệu không:

1. **Gọi trực tiếp API:**
   ```bash
   curl -s "http://localhost:80/api/hybrid/video_data?url=https://www.douyin.com/jingxuan?modal_id=7621115321297980672&minimal=false"
   ```
2. **Kỳ vọng:** Phản hồi trả về có status code `200` và chứa dữ liệu có cấu trúc dạng:
   ```json
   {
     "code": 200,
     "router": "/api/hybrid/video_data",
     "data": {
       "desc": "Tiêu đề video...",
       "author": { "nickname": "Tên tác giả" },
       "video_data": {
         "nwm_video_url_HQ": "http://aweme.snssdk.com/..."
       }
     }
   }
   ```
3. **Thử nghiệm trên UI:** Mở file giao diện test `temp_snap.html` hoặc giao diện chính của **Tải Mọi Thứ**, dán link Douyin và nhấn nút tải để đảm bảo toàn bộ luồng từ UI -> Backend -> Local API -> Trình tải hoạt động trơn tru.
