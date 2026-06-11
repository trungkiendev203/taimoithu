import subprocess

VPS_IP = "98.81.205.79"
VPS_USER = "ubuntu"
# Generate sslip.io domain based on IP
DOMAIN = f"{VPS_IP.replace('.', '-')}.sslip.io"
EMAIL = "trungkiendev203@gmail.com"

def configure_nginx_and_ssl():
    print(f"=== 1. Đang cấu hình Nginx cho Domain: {DOMAIN} ===")
    
    # Nginx configuration content
    nginx_config = f"""
server {{
    listen 80;
    server_name {DOMAIN};

    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
    # Write configuration locally
    local_nginx_cfg = "taimoithu_nginx_ssl.conf"
    with open(local_nginx_cfg, "w", encoding="utf-8") as f:
        f.write(nginx_config)
        
    # Upload configuration to VPS
    print("-> Đang tải file cấu hình Nginx lên VPS...")
    scp_cmd = f'scp -o StrictHostKeyChecking=no {local_nginx_cfg} {VPS_USER}@{VPS_IP}:/home/ubuntu/taimoithu_nginx_ssl.conf'
    subprocess.run(scp_cmd, shell=True)
    
    # Clean up local file
    import os
    if os.path.exists(local_nginx_cfg):
        os.remove(local_nginx_cfg)

    print("\n=== 2. Cài đặt Nginx & Cấp chứng chỉ SSL HTTPS qua Certbot ===")
    
    commands = [
        "sudo apt-get update -y",
        "sudo apt-get install -y nginx certbot python3-certbot-nginx",
        "sudo cp /home/ubuntu/taimoithu_nginx_ssl.conf /etc/nginx/sites-available/taimoithu_ssl",
        "sudo ln -sf /etc/nginx/sites-available/taimoithu_ssl /etc/nginx/sites-enabled/",
        "sudo rm -f /etc/nginx/sites-enabled/default",
        "sudo nginx -t",
        "sudo systemctl restart nginx",
        f"sudo certbot --nginx -d {DOMAIN} --non-interactive --agree-tos --email {EMAIL} --redirect",
        "sudo systemctl reload nginx"
    ]
    remote_commands = " && ".join(commands)
    
    ssh_cmd = f'ssh -o StrictHostKeyChecking=no {VPS_USER}@{VPS_IP} "{remote_commands}"'
    res = subprocess.run(ssh_cmd, shell=True)
    
    if res.returncode == 0:
        print("\n=== THIẾT LẬP HTTPS THÀNH CÔNG! ===")
        print(f"Backend API (HTTPS) của bạn hiện đang chạy tại: https://{DOMAIN}")
        print("Bây giờ bạn có thể kết nối với Vercel một cách an toàn!")
    else:
        print("\nLỗi: Quá trình thiết lập HTTPS hoặc cấp SSL gặp sự cố.")

if __name__ == "__main__":
    configure_nginx_and_ssl()
