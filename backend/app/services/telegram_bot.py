import os
import glob
import shutil
import time
import tempfile
import telebot
from datetime import datetime
from threading import Thread

from app.core.config import settings
from app.core.logger import logger
from app.services.helpers import get_cookies_file_path
from app.services.ytdlp_service import execute_with_fallback, get_base_ydl_opts
import http.cookiejar

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN) if settings.TELEGRAM_BOT_TOKEN else None
ADMIN_ID = str(settings.TELEGRAM_ADMIN_ID) if settings.TELEGRAM_ADMIN_ID else None

TEST_BILI_URL = "https://www.bilibili.com/video/BV15x4y1t7D7"  # Video luôn có 1080p

def get_file_last_modified(file_path):
    if not file_path or not os.path.exists(file_path):
        return "N/A"
    mtime = os.path.getmtime(file_path)
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")

def verify_cookie_status():
    """Kiểm tra trạng thái của cookie và chất lượng tối đa có thể tải."""
    try:
        base_opts = get_base_ydl_opts('bilibili')
        info, _ = execute_with_fallback(TEST_BILI_URL, 'bilibili', base_opts, download=False)
        
        resolutions = []
        for f in info.get("formats", []):
            h = f.get("height")
            vcodec = f.get("vcodec", "none")
            if h and h > 0 and vcodec != "none":
                resolutions.append(h)
                
        if resolutions:
            max_res = max(resolutions)
            return True, f"{max_res}p"
        return False, "Unknown"
    except Exception as e:
        logger.error(f"Error checking cookie status: {e}")
        return False, str(e)


def verify_ig_cookie_status():
    """Kiểm tra trạng thái của cookie Instagram."""
    try:
        cookie_path = get_cookies_file_path(prefix="ig_cookies")
        if not cookie_path:
            return False, "Not Found"
        cj = http.cookiejar.MozillaCookieJar(cookie_path)
        cj.load(ignore_discard=True, ignore_expires=True)
        has_ig = any("instagram.com" in cookie.domain for cookie in cj)
        if has_ig:
            return True, "Valid format & Contains IG cookies"
        return False, "No IG cookies found"
    except Exception as e:
        logger.error(f"Error checking IG cookie status: {e}")
        return False, str(e)


def is_admin(message):
    if not ADMIN_ID:
        return False
    return str(message.from_user.id) == ADMIN_ID


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not is_admin(message):
        return
    help_text = (
        "Bilibili & IG Cookie Manager\n"
        "/status - Kiểm tra trạng thái Bilibili & IG\n"
        "/rollback_cookie - Khôi phục cookie Bilibili cũ\n"
        "/rollback_ig_cookie - Khôi phục cookie IG cũ\n"
        "Để cập nhật, chỉ cần gửi file .txt (Nếu tên file có chứa 'ig' sẽ lưu thành IG Cookie)"
    )
    bot.reply_to(message, help_text)


@bot.message_handler(commands=['status'])
def send_status(message):
    if not is_admin(message):
        return
    bot.reply_to(message, "Đang kiểm tra trạng thái cookie, vui lòng đợi...")
    
    # Bilibili
    success_bili, quality_bili = verify_cookie_status()
    cookie_file_bili = get_cookies_file_path(prefix="cookies")
    bili_found = "FOUND" if cookie_file_bili else "NOT FOUND"
    bili_valid = "VALID" if success_bili and quality_bili not in ["Unknown"] else "INVALID"
    bili_time = get_file_last_modified(cookie_file_bili)
    
    # Instagram
    success_ig, msg_ig = verify_ig_cookie_status()
    cookie_file_ig = get_cookies_file_path(prefix="ig_cookies")
    ig_found = "FOUND" if cookie_file_ig else "NOT FOUND"
    ig_valid = "VALID" if success_ig else "INVALID"
    ig_time = get_file_last_modified(cookie_file_ig)
    
    response = (
        "Instagram:\n"
        f"* File: {ig_found}\n"
        f"* Session: {ig_valid}\n"
        f"* Last Update: {ig_time}\n\n"
        "Bilibili:\n"
        f"* File: {bili_found}\n"
        f"* Session: {bili_valid}\n"
        f"* Last Update: {bili_time}"
    )
    bot.reply_to(message, response)


@bot.message_handler(commands=['rollback_cookie'])
def rollback_cookie(message):
    if not is_admin(message):
        return
        
    backup_dir = os.path.abspath("backend/backups") if os.path.exists("backend") else os.path.abspath("backups")
    if not os.path.exists(backup_dir):
        bot.reply_to(message, "Không tìm thấy thư mục backup.")
        return
        
    backups = sorted(glob.glob(os.path.join(backup_dir, "cookies_*.txt")), reverse=True)
    if not backups:
        bot.reply_to(message, "Không có file backup nào để khôi phục.")
        return
        
    latest_backup = backups[0]
    target_path = os.path.abspath("backend/cookies.txt") if os.path.exists("backend") else os.path.abspath("cookies.txt")
    
    try:
        shutil.copy2(latest_backup, target_path)
        bot.reply_to(message, f"Đã khôi phục cookie thành công từ: {os.path.basename(latest_backup)}\nDùng /status để kiểm tra.")
    except Exception as e:
        bot.reply_to(message, f"Lỗi khôi phục: {str(e)}")


@bot.message_handler(commands=['rollback_ig_cookie'])
def rollback_ig_cookie(message):
    if not is_admin(message):
        return
        
    backup_dir = os.path.abspath("backend/backups") if os.path.exists("backend") else os.path.abspath("backups")
    if not os.path.exists(backup_dir):
        bot.reply_to(message, "Không tìm thấy thư mục backup.")
        return
        
    backups = sorted(glob.glob(os.path.join(backup_dir, "ig_cookies_*.txt")), reverse=True)
    if not backups:
        bot.reply_to(message, "Không có file backup IG nào để khôi phục.")
        return
        
    latest_backup = backups[0]
    target_path = os.path.abspath("backend/ig_cookies.txt") if os.path.exists("backend") else os.path.abspath("ig_cookies.txt")
    
    try:
        shutil.copy2(latest_backup, target_path)
        bot.reply_to(message, f"Đã khôi phục IG cookie thành công từ: {os.path.basename(latest_backup)}\nDùng /status để kiểm tra.")
    except Exception as e:
        bot.reply_to(message, f"Lỗi khôi phục: {str(e)}")


@bot.message_handler(content_types=['document'])
def handle_cookie_document(message):
    if not is_admin(message):
        return
        
    if not message.document.file_name.endswith('.txt'):
        bot.reply_to(message, "Từ chối: Vui lòng gửi file cookies có định dạng .txt")
        return
        
    # Security: Limit file size to 1MB (1048576 bytes)
    if message.document.file_size > 1048576:
        bot.reply_to(message, "Từ chối: File quá lớn. Kích thước tối đa là 1MB.")
        return
        
    try:
        bot.reply_to(message, "Đang phân tích và validate file cookie...")
        
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Save to temporary file
        fd, temp_path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, 'wb') as f:
            f.write(downloaded_file)
            
        content_text = downloaded_file.decode('utf-8', errors='ignore').strip()
        if content_text.startswith('['):
            from app.services.helpers import convert_json_to_netscape
            converted_path = temp_path + "_converted.txt"
            if convert_json_to_netscape(temp_path, converted_path):
                os.remove(temp_path)
                temp_path = converted_path
            else:
                os.remove(temp_path)
                bot.reply_to(message, "Từ chối: File tải lên giống JSON nhưng không thể convert sang Netscape chuẩn.")
                return
        else:
            # Tự động thêm header Netscape nếu file bị thiếu
            if not downloaded_file.startswith(b"# Netscape HTTP Cookie File"):
                with open(temp_path, 'wb') as f:
                    f.write(b"# Netscape HTTP Cookie File\n\n")
                    f.write(downloaded_file)
            
        # Validate format using MozillaCookieJar
        cj = http.cookiejar.MozillaCookieJar(temp_path)
        try:
            cj.load(ignore_discard=True, ignore_expires=True)
        except Exception as e:
            os.remove(temp_path)
            bot.reply_to(message, f"Từ chối: File không đúng định dạng Netscape Cookie File. Lỗi: {str(e)}")
            return
            
        has_ig = any("instagram.com" in c.domain and c.name == "sessionid" for c in cj)
        has_bili = any("bilibili.com" in c.domain and c.name == "SESSDATA" for c in cj)
        
        if has_ig:
            prefix = "ig_cookies"
            platform_msg = "Instagram"
        elif has_bili:
            prefix = "cookies"
            platform_msg = "Bilibili"
        else:
            os.remove(temp_path)
            bot.reply_to(message, "Từ chối: Định dạng đúng nhưng không tìm thấy sessionid (IG) hoặc SESSDATA (Bilibili).")
            return
            
        target_path = os.path.abspath(f"backend/{prefix}.txt") if os.path.exists("backend") else os.path.abspath(f"{prefix}.txt")
        
        # Backup cũ nếu có
        if os.path.exists(target_path):
            backup_dir = os.path.abspath("backend/backups") if os.path.exists("backend") else os.path.abspath("backups")
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"{prefix}_{timestamp}.txt")
            shutil.copy2(target_path, backup_path)
            
        # Atomic replace
        shutil.move(temp_path, target_path)
        
        bot.reply_to(message, f"Đã nhận diện và lưu cookie cho {platform_msg}. Đang kiểm tra tính hợp lệ...")
        
        if has_ig:
            success, status_msg = verify_ig_cookie_status()
            bot.reply_to(message, f"Kết quả kiểm tra IG cookie mới:\nTrạng thái: {status_msg}")
        else:
            success, quality = verify_cookie_status()
            bot.reply_to(message, f"Kết quả kiểm tra Bilibili cookie mới:\nMax Quality: {quality}")
            
    except Exception as e:
        logger.error(f"Telegram file handling error: {e}")
        bot.reply_to(message, f"Lỗi không xác định khi xử lý file: {str(e)}")


def run_telegram_bot():
    if not bot:
        logger.info("Telegram Bot Token is not set. Bot is disabled.")
        return
    logger.info("Starting Telegram Bot Polling...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            logger.error(f"Telegram bot polling crashed: {e}")
            time.sleep(10)

def start_telegram_bot_thread():
    if settings.TELEGRAM_BOT_TOKEN:
        thread = Thread(target=run_telegram_bot, daemon=True)
        thread.start()

def check_cookie_periodic():
    if not bot or not ADMIN_ID:
        return
        
    # Check Bilibili
    success_bili, quality_bili = verify_cookie_status()
    cookie_file_bili = get_cookies_file_path(prefix="cookies")
    
    bili_issue = None
    if not cookie_file_bili:
        bili_issue = "Cookie không tồn tại"
    elif quality_bili in ["Unknown"] or (type(quality_bili) == str and not quality_bili.endswith('p')):
        bili_issue = "Lỗi không xác định khi lấy chất lượng"
    else:
        try:
            res_val = int(quality_bili.replace('p', ''))
            if res_val < 720:
                bili_issue = "Cookie có thể đã hết hạn (Chất lượng tối đa giảm xuống dưới 720p)"
        except:
            pass
            
    # Check Instagram
    success_ig, msg_ig = verify_ig_cookie_status()
    ig_issue = None
    if not success_ig:
        ig_issue = f"Lỗi xác thực hoặc không tìm thấy: {msg_ig}"
            
    if bili_issue or ig_issue:
        warning_msg = "⚠️ *Cookie Warning!*\n\n"
        if bili_issue:
            warning_msg += f"📺 *Bilibili:*\n- Vấn đề: {bili_issue}\n- Chất lượng hiện tại: {quality_bili}\n\n"
        if ig_issue:
            warning_msg += f"📸 *Instagram:*\n- Vấn đề: {ig_issue}"
            
        try:
            bot.send_message(ADMIN_ID, warning_msg, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Failed to send warning via Telegram: {e}")
