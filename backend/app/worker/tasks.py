import os
import shutil
import yt_dlp
from typing import Dict, Any
from app.core.celery_app import celery_app
from app.core.redis_helper import redis_helper
from app.schemas.job import JobState
from app.core.logger import logger

def publish_progress(job_id: str, status: str, progress: float, speed: float = None, eta: int = None, download_url: str = None, error_msg: str = None):
    state = JobState(
        job_id=job_id,
        status=status,
        progress=progress,
        speed_bytes=speed,
        eta_seconds=eta,
        download_url=download_url,
        error_message=error_msg
    ).model_dump()
    
    redis_helper.set_job_state(job_id, state)
    redis_helper.publish_job_event(job_id, state)

from yt_dlp.networking.impersonate import ImpersonateTarget
import time
from app.core.config import settings

@celery_app.task(bind=True, name="app.worker.tasks.download_video_task")
def download_video_task(self, job_id: str, url: str, format_id: str, tier: str = "free", item_index: int = None):
    logger.info(f"Starting job {job_id} for URL {url} [Tier: {tier}]")
    
    download_dir = os.path.abspath(f"downloads/{job_id}")
    os.makedirs(download_dir, exist_ok=True)
    
    output_template = os.path.join(download_dir, '%(title)s.%(ext)s')
    
    start_time = time.time()
    
    # limits
    max_size_mb = settings.PREMIUM_MAX_FILE_SIZE_MB if tier == "premium" else settings.FREE_MAX_FILE_SIZE_MB
    max_size_bytes = max_size_mb * 1024 * 1024
    duration_limit = 3600
    
    def progress_hook(d: Dict[str, Any]):
        # 1. Enforce time limit
        elapsed = time.time() - start_time
        if elapsed > duration_limit:
            raise Exception(f"Quá thời gian tải tối đa cho phép ({duration_limit} giây).")
            
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            
            # 2. Enforce file size limit
            if total > max_size_bytes:
                raise Exception(f"Kích thước file vượt quá giới hạn cho phép ({max_size_mb} MB).")
            if downloaded > max_size_bytes:
                raise Exception(f"Dung lượng đã tải vượt quá giới hạn cho phép ({max_size_mb} MB).")
                
            if total > 0:
                progress = round((downloaded / total) * 100, 2)
                speed = d.get('speed')
                eta = d.get('eta')
                publish_progress(job_id, "PROCESSING", progress, speed, eta)
        elif d['status'] == 'finished':
            publish_progress(job_id, "PROCESSING", 100.0) # merging

    ydl_opts = {
        'format': format_id,
        'outtmpl': output_template,
        'progress_hooks': [progress_hook],
        'quiet': True,
        'no_warnings': True,
        'ignore_no_formats_error': True,
        'merge_output_format': 'mp4',
        'concurrent_fragment_downloads': 5,
        'impersonate': ImpersonateTarget.from_str('chrome'),
        # Cấu hình đầy đủ JavaScript runtime và giải quyết các giới hạn chặn để tải đầy đủ độ phân giải (1080p, 720p,...)
        'js_runtimes': {'node': {}},
        'remote_components': ['ejs:github'],
        'extractor_args': {
            'youtube': {
                'player_client': ['default', '-tv', 'web_safari', 'web_embedded']
            }
        },
        'logger': logger,  # Tích hợp logger của ứng dụng vào yt-dlp để thu thập log tốt hơn
    }
    
    from app.services.helpers import get_cookies_file_path
    cookiefile = get_cookies_file_path()
    if cookiefile:
        ydl_opts['cookiefile'] = cookiefile
    
    if item_index is not None:
        ydl_opts['playlist_items'] = str(item_index)
        
    is_custom_thumbnail = (format_id == 'custom_image_thumbnail')
    if is_custom_thumbnail:
        ydl_opts['skip_download'] = True
        ydl_opts['writethumbnail'] = True
        # Set format back to a valid one so yt-dlp doesn't fail parsing format string
        ydl_opts['format'] = 'best'
        
    final_file = None
    try:
        publish_progress(job_id, "PROCESSING", 0.0)
        
        if format_id.startswith('direct_url:'):
            import base64
            import requests
            from app.services.platform_detector import detect_platform
            from app.services.helpers import PLATFORM_REFERER_MAP
            
            publish_progress(job_id, "PROCESSING", 10.0, None, None)
            
            encoded_url = format_id.split('direct_url:')[1]
            # Tương thích ngược: đổi khoảng trắng thành +
            encoded_url = encoded_url.replace(" ", "+")
            # Thêm padding nếu thiếu
            encoded_url += "=" * ((-len(encoded_url)) % 4)
            direct_url = base64.urlsafe_b64decode(encoded_url).decode('utf-8')
            
            # Detect platform để gửi đúng Referer (Douyin CDN chặn referer sai)
            try:
                dl_platform = detect_platform(url)
            except Exception:
                dl_platform = "unknown"
            referer = PLATFORM_REFERER_MAP.get(dl_platform, 'https://www.google.com/')
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': referer
            }
            response = requests.get(direct_url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            total_length = response.headers.get('content-length')
            
            # Determine extension
            ext = 'mp4' if 'video' in response.headers.get('content-type', '') else 'jpg'
            final_file = os.path.join(download_dir, f"media_download.{ext}")
            
            with open(final_file, "wb") as f:
                if total_length is None:
                    f.write(response.content)
                    publish_progress(job_id, "PROCESSING", 90.0, None, None)
                else:
                    dl = 0
                    total_length = int(total_length)
                    last_progress = 0
                    # Chunk size 1MB để I/O đĩa nhanh hơn
                    for data in response.iter_content(chunk_size=1024*1024):
                        dl += len(data)
                        f.write(data)
                        progress = round((dl / total_length) * 100, 2)
                        # Chỉ update Redis khi tiến trình tăng ít nhất 5% để chống nghẽn cổ chai
                        if progress - last_progress >= 5.0 or progress == 100.0:
                            publish_progress(job_id, "PROCESSING", progress, None, None)
                            last_progress = progress
        else:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                # Tên file thực tế sau khi tải (có thể đổi đuôi mkv/mp4)
                final_file = ydl.prepare_filename(info)
                if ydl_opts.get('merge_output_format'):
                    base, _ = os.path.splitext(final_file)
                    final_file = f"{base}.{ydl_opts['merge_output_format']}"

        if is_custom_thumbnail:
            # yt-dlp writes thumbnail with various extensions (.jpg, .webp). We must find it in the dir.
            import glob
            possible_files = glob.glob(os.path.join(download_dir, '*'))
            if possible_files:
                final_file = possible_files[0]
            else:
                raise Exception("Không tìm thấy ảnh bìa được tải về.")
        else:
            if not os.path.exists(final_file):
                raise Exception("File tải về không tồn tại.")
            
        filename = os.path.basename(final_file)
        # Vì lưu vào `downloads/{job_id}/filename`, đường dẫn trả về sẽ là:
        download_url = f"/static/downloads/{job_id}/{filename}"
        
        publish_progress(job_id, "COMPLETED", 100.0, download_url=download_url)
        logger.info(f"Job {job_id} completed successfully.")
        
    except yt_dlp.utils.ExtractorError as e:
        logger.error(f"ExtractorError during download {job_id}: {str(e)}")
        error_msg = "Không tìm thấy định dạng video/ảnh khả dụng để tải về. Bài đăng có thể bị giới hạn hoặc không hỗ trợ." if "No video formats found" in str(e) else f"Lỗi trích xuất: {str(e)}"
        publish_progress(job_id, "FAILED", 0.0, error_msg=error_msg)
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir, ignore_errors=True)
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        publish_progress(job_id, "FAILED", 0.0, error_msg=str(e))
        # Dọn dẹp ngay nếu lỗi
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir, ignore_errors=True)
    finally:
        # Giải phóng active job cho IP này
        try:
            redis_helper.remove_active_job(job_id)
        except Exception as ex:
            logger.error(f"Failed to remove active job {job_id} from Redis: {ex}")

@celery_app.task(name="app.worker.tasks.cleanup_downloads_task")
def cleanup_downloads_task():
    """
    Task định kỳ để dọn dẹp thư mục downloads
    """
    from app.utils.cleanup import cleanup_old_files
    cleanup_old_files()
