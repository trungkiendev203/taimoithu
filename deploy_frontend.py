import os
import sys
import zipfile
import subprocess
import shutil

VPS_IP = "98.81.205.79"
VPS_USER = "ubuntu"
REMOTE_DIR = "/home/ubuntu/taimoithu"

def build_frontend():
    print("=== 1. Đang cài đặt thư viện và build Frontend locally ===")
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    if not os.path.exists(frontend_dir):
        print("Lỗi: Không tìm thấy thư mục frontend.")
        return False
    
    # Run npm install
    print("-> Chạy npm install...")
    subprocess.run("npm install", shell=True, cwd=frontend_dir)
    
    # Run npm run build with VITE_API_BASE_URL=/api/v1
    print("-> Chạy npm run build với relative API base...")
    # Set env variable in PowerShell/CMD style
    build_cmd = 'set VITE_API_BASE_URL=/api/v1&& npm run build'
    if sys.platform != "win32":
         build_cmd = 'VITE_API_BASE_URL=/api/v1 npm run build'
         
    res = subprocess.run(build_cmd, shell=True, cwd=frontend_dir)
    if res.returncode != 0:
        print("Lỗi: Build frontend thất bại.")
        return False
        
    dist_dir = os.path.join(frontend_dir, "dist")
    if not os.path.exists(dist_dir):
        print("Lỗi: Thư mục build 'dist' không được tạo.")
        return False
        
    print("-> Build Frontend thành công!")
    return dist_dir

def zip_dist(dist_dir):
    print("\n=== 2. Đang nén thư mục build dist ===")
    zip_path = "frontend.zip"
    if os.path.exists(zip_path):
        os.remove(zip_path)
        
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Store relative to dist
                arcname = os.path.relpath(file_path, dist_dir)
                zipf.write(file_path, arcname)
                
    print(f"-> Đã nén thành công vào file: {zip_path}")
    return zip_path

def upload_and_deploy_frontend(zip_path):
    print("\n=== 3. Đang tải Frontend lên máy chủ VPS ===")
    # Copy zip to VPS
    scp_cmd = f'scp -o StrictHostKeyChecking=no {zip_path} {VPS_USER}@{VPS_IP}:{REMOTE_DIR}/frontend.zip'
    
    # Ensure directory exists on VPS
    ssh_mkdir = f'ssh -o StrictHostKeyChecking=no {VPS_USER}@{VPS_IP} "mkdir -p {REMOTE_DIR}/frontend"'
    subprocess.run(ssh_mkdir, shell=True)
    
    res = subprocess.run(scp_cmd, shell=True)
    if res.returncode != 0:
        print("Lỗi: Không thể tải Frontend lên VPS.")
        return False
    print("-> Tải tệp tin lên VPS thành công!")
    
    print("\n=== 4. Đang cài đặt và cấu hình Nginx trên VPS ===")
    nginx_config = """
server {
    listen 80;
    server_name _;

    location / {
        root """ + REMOTE_DIR + """/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""
    # Write nginx config locally to upload
    local_nginx_cfg = "taimoithu_nginx.conf"
    with open(local_nginx_cfg, "w", encoding="utf-8") as f:
        f.write(nginx_config)
        
    # Upload nginx config
    scp_nginx = f'scp -o StrictHostKeyChecking=no {local_nginx_cfg} {VPS_USER}@{VPS_IP}:{REMOTE_DIR}/taimoithu_nginx.conf'
    subprocess.run(scp_nginx, shell=True)
    if os.path.exists(local_nginx_cfg):
        os.remove(local_nginx_cfg)

    # Shell commands to set up Nginx, unzip frontend, and restart Nginx
    remote_commands = f"""
    sudo apt-get update -y && sudo apt-get install -y nginx unzip
    cd {REMOTE_DIR}/frontend
    rm -rf dist
    mkdir -p dist
    unzip -o ../frontend.zip -d dist/
    
    # Configure Nginx
    sudo cp ../taimoithu_nginx.conf /etc/nginx/sites-available/taimoithu
    sudo ln -sf /etc/nginx/sites-available/taimoithu /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test and restart Nginx
    sudo nginx -t && sudo systemctl restart nginx
    """
    
    ssh_nginx = f'ssh -o StrictHostKeyChecking=no {VPS_USER}@{VPS_IP} "{remote_commands}"'
    subprocess.run(ssh_nginx, shell=True)
    
    print("\n=== HOÀN THÀNH TRIỂN KHAI FRONTEND & NGINX! ===")
    print(f"Hệ thống của bạn đã online hoàn toàn tại: http://{VPS_IP}")
    print("Bạn có thể truy cập IP trên trình duyệt để sử dụng trang web ngay lập tức!")
    return True

if __name__ == "__main__":
    dist_dir = build_frontend()
    if dist_dir:
        zip_path = zip_dist(dist_dir)
        success = upload_and_deploy_frontend(zip_path)
        if os.path.exists(zip_path):
            os.remove(zip_path)
