# Hướng dẫn Triển khai (Deployment) Hệ thống "Tải Mọi Thứ"

Hệ thống của bạn bao gồm 2 phần riêng biệt: **Frontend** (React/Vite) và **Backend** (FastAPI + Redis + Celery + Evil0ctal). Để đưa hệ thống lên mạng cho mọi người sử dụng thực tế (Production), phương án **tối ưu, tiết kiệm và dễ bảo trì nhất** hiện nay là:

1. **Frontend:** Chạy trên **Vercel** hoặc **Cloudflare Pages** (Miễn phí hoàn toàn, siêu nhanh, tự động có HTTPS, chống DDoS tốt).
2. **Backend:** Chạy trên **1 máy chủ VPS Linux (Ubuntu)** bằng Docker Compose.

Dưới đây là các bước chi tiết:

---

## BƯỚC 1: Chuẩn bị tài nguyên

1. **Mua Tên miền (Domain):** Mua tại Namecheap, Tenten, Inet, v.v. (Ví dụ: `taimoithu.com`).
2. **Mua VPS:** Thuê một VPS (Cloud Server) chạy hệ điều hành **Ubuntu 22.04 LTS**.
   - Cấu hình đề nghị: Tối thiểu 2 CPU, 2GB RAM (khuyên dùng 4GB RAM vì có chạy Docker và Worker tải video lớn).
   - Nhà cung cấp: *DigitalOcean, Vultr, Hetzner, Vietnix...*

---

## BƯỚC 2: Triển khai Frontend lên Vercel (Miễn phí & Tự động)

Vercel là nền tảng số 1 hiện nay cho các ứng dụng React/Vite.

1. Tải code của bạn lên một **GitHub / GitLab repository** (Nên set Private).
2. Truy cập [Vercel.com](https://vercel.com) và đăng nhập bằng GitHub.
3. Bấm **"Add New Project"** -> Chọn Repository chứa code của bạn.
4. Ở phần **Framework Preset**, Vercel sẽ tự nhận diện là **Vite**.
5. Ở phần **Root Directory**, chọn thư mục `frontend` (vì code frontend nằm trong thư mục này).
6. Ở phần **Environment Variables**, thêm biến môi trường gọi tới Backend (tạm thời điền domain backend bạn dự tính, ví dụ: `VITE_API_URL=https://api.taimoithu.com`).
7. Bấm **Deploy**. Vercel sẽ tự động chạy lệnh `npm run build` và public website lên mạng.
8. Trỏ Tên miền (Domain chính) của bạn về Vercel trong tab *Settings > Domains*.

---

## BƯỚC 3: Triển khai Backend lên VPS

Bạn sẽ cài đặt Docker và chạy Backend trên VPS.

### 3.1. Cài đặt Docker trên VPS
Mở Terminal/SSH vào VPS và chạy lệnh sau để cài đặt Docker và Docker Compose:
```bash
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker
sudo systemctl start docker
```

### 3.2. Đưa code lên VPS
Tạo một thư mục chứa dự án và tải mã nguồn (thư mục `backend` và file `docker-compose.yml`) lên VPS (có thể dùng `git clone` hoặc FileZilla/WinSCP).
```bash
mkdir -p /root/taimoithu
cd /root/taimoithu
```

### 3.3. Tạo file `docker-compose.prod.yml`
Hiện tại `docker-compose.yml` đang dùng cho việc dev (ví dụ `uvicorn --reload`). Trên VPS, hãy tạo một file `docker-compose.prod.yml` chuyên cho Production, bỏ đi Frontend (vì Frontend đã chạy trên Vercel):

```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    restart: always
    ports:
      - "127.0.0.1:6379:6379"

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    ports:
      - "127.0.0.1:8000:8000"
    env_file:
      - ./backend/.env
    environment:
      - REDIS_URL=redis://redis:6379/0
      - EVIL0CTAL_URL=http://evil0ctal:80
    depends_on:
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    env_file:
      - ./backend/.env
    environment:
      - REDIS_URL=redis://redis:6379/0
      - EVIL0CTAL_URL=http://evil0ctal:80
    depends_on:
      - redis
    command: celery -A app.core.celery_app worker --loglevel=info --concurrency=4

  evil0ctal:
    image: evil0ctal/douyin_tiktok_download_api:latest
    restart: always
```

### 3.4. Cấu hình CORS và Môi trường
Mở file `/root/taimoithu/backend/.env` trên VPS và đảm bảo đã sửa dòng này để cho phép Vercel gọi API:
```env
BACKEND_CORS_ORIGINS=["https://taimoithu.com", "https://www.taimoithu.com"]
DEBUG=False
```

### 3.5. Chạy Backend
Khởi động hệ thống:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```
Kiểm tra xem các container đã chạy ổn định chưa bằng lệnh `docker ps`.

---

## BƯỚC 4: Trỏ tên miền phụ cho API (Nginx + SSL)

Bạn không thể để Frontend (HTTPS) gọi API (HTTP qua cổng 8000) được vì trình duyệt sẽ chặn (Lỗi Mixed Content). Cần cài **Nginx** và cấp **SSL (HTTPS)** miễn phí bằng Certbot.

1. **Trỏ tên miền:** Trỏ một subdomain (ví dụ: `api.taimoithu.com`) về IP của VPS.
2. **Cài đặt Nginx & Certbot:**
```bash
sudo apt install nginx certbot python3-certbot-nginx -y
```
3. **Cấu hình Nginx:** Tạo file `/etc/nginx/sites-available/api.taimoithu.com` với nội dung:
```nginx
server {
    server_name api.taimoithu.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
4. Kích hoạt cấu hình:
```bash
sudo ln -s /etc/nginx/sites-available/api.taimoithu.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```
5. Cài SSL (HTTPS):
```bash
sudo certbot --nginx -d api.taimoithu.com
```

---

## BƯỚC 5: Kết nối Frontend và Backend

Cuối cùng, quay lại **Vercel** -> vào phần **Settings** -> **Environment Variables** -> Sửa lại biến `VITE_API_URL` thành:
```text
VITE_API_URL=https://api.taimoithu.com/api/v1
```
(Sau khi sửa, nhớ Redploy lại trên Vercel để hệ thống nhận biến mới).

**🎉 HOÀN THÀNH!**
Bây giờ mọi người truy cập vào `https://taimoithu.com` (Vercel) -> Hệ thống sẽ gọi API tải video một cách bảo mật tới `https://api.taimoithu.com` (VPS). Chúc bạn thành công!
