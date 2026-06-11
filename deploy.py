import os
import sys
import zipfile
import subprocess
import shutil

VPS_IP = "98.81.205.79"
VPS_USER = "ubuntu"
REMOTE_DIR = "/home/ubuntu/taimoithu"

def zip_backend():
    print("=== 1. Đang nén thư mục backend và file cấu hình ===")
    zip_path = "deploy.zip"
    if os.path.exists(zip_path):
        os.remove(zip_path)

    # File to include directly in the zip root
    files_to_include = {
        "docker-compose.prod.yml": "docker-compose.prod.yml"
    }

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add root config files
        for local_file, zip_name in files_to_include.items():
            if os.path.exists(local_file):
                zipf.write(local_file, zip_name)
        
        # Add backend folder
        for root, dirs, files in os.walk("backend"):
            # Exclude venv, pycache, git, etc.
            if "venv" in root or "__pycache__" in root or ".git" in root or "node_modules" in root:
                continue
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, file_path)
    
    print(f"-> Đã nén thành công vào file: {zip_path}")
    return zip_path

def upload_and_deploy(zip_path):
    print("\n=== 2. Đang tải tệp tin lên máy chủ VPS ===")
    # Copy zip to VPS
    scp_cmd = f'scp -o StrictHostKeyChecking=no {zip_path} {VPS_USER}@{VPS_IP}:{REMOTE_DIR}/deploy.zip'
    
    # Pre-create remote directory
    ssh_mkdir = f'ssh -o StrictHostKeyChecking=no {VPS_USER}@{VPS_IP} "mkdir -p {REMOTE_DIR}"'
    subprocess.run(ssh_mkdir, shell=True)
    
    # Run SCP
    res = subprocess.run(scp_cmd, shell=True)
    if res.returncode != 0:
        print("Lỗi: Không thể tải tệp tin lên VPS. Vui lòng kiểm tra lại kết nối SSH.")
        return False
        
    print("-> Tải tệp tin lên VPS thành công!")
    
    print("\n=== 3. Đang cài đặt và chạy Docker trên VPS ===")
    # Flatten commands into a single line to prevent Windows OpenSSH from entering interactive mode
    commands = [
        "sudo apt-get update -y",
        "sudo apt-get install -y unzip docker.io docker-compose",
        "sudo systemctl enable docker",
        "sudo systemctl start docker",
        "sudo usermod -aG docker ubuntu",
        f"cd {REMOTE_DIR}",
        "unzip -o deploy.zip",
        "sudo docker compose -f docker-compose.prod.yml down || true",
        "sudo docker compose -f docker-compose.prod.yml up -d --build"
    ]
    remote_commands = " && ".join(commands)
    
    ssh_deploy = f'ssh -o StrictHostKeyChecking=no {VPS_USER}@{VPS_IP} "{remote_commands}"'
    subprocess.run(ssh_deploy, shell=True)
    print("\n=== HOÀN THÀNH TRIỂN KHAI BACKEND! ===")
    print(f"Backend của bạn hiện đang chạy tại: http://{VPS_IP}:8000")
    print("Bạn có thể cấu hình Nginx và SSL tiếp tục theo file DEPLOYMENT_GUIDE.md")
    return True

if __name__ == "__main__":
    if not os.path.exists("backend"):
        print("Lỗi: Không tìm thấy thư mục backend ở thư mục hiện tại.")
        sys.exit(1)
        
    zip_path = zip_backend()
    success = upload_and_deploy(zip_path)
    
    # Clean up local zip
    if os.path.exists(zip_path):
        os.remove(zip_path)
