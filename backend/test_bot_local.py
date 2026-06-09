import os
import shutil
from unittest.mock import MagicMock

# Force settings
os.environ["TELEGRAM_BOT_TOKEN"] = "123456:mock_token"

from app.services.telegram_bot import send_status, handle_cookie_document, rollback_cookie, get_cookies_file_path

def test_telegram_workflow():
    print("\n--- 1. /status trước khi có cookie ---")
    cookie_path = "backend/cookies.txt" if os.path.exists("backend") else "cookies.txt"
    if os.path.exists(cookie_path): os.remove(cookie_path)
    
    msg_status_1 = MagicMock()
    msg_status_1.from_user.id = 12345
    # Force admin id match
    import app.services.telegram_bot as tb
    tb.ADMIN_ID = "12345"
    
    # Mock bot.reply_to
    tb.bot.reply_to = lambda msg, text: print(f"[Bot Reply]: {text}")
    
    send_status(msg_status_1)
    
    print("\n--- 2. /update_cookie ---")
    msg_update = MagicMock()
    msg_update.from_user.id = 12345
    msg_update.document.file_name = "cookies.txt"
    msg_update.document.file_size = 500
    msg_update.document.file_id = "test_file_id"
    
    # Mock bot file download
    tb.bot.get_file = lambda file_id: MagicMock(file_path="mock_path")
    # Provide a fake cookie content
    fake_cookie = b"# Netscape HTTP Cookie File\n.bilibili.com\tTRUE\t/\tFALSE\t1799999999\tSESSDATA\tfake_session\n"
    tb.bot.download_file = lambda file_path: fake_cookie
    
    handle_cookie_document(msg_update)
    
    print("\n--- 3. /status sau khi upload ---")
    send_status(msg_status_1)
    
    print("\n--- 4. /rollback_cookie ---")
    rollback_cookie(msg_status_1)

if __name__ == "__main__":
    test_telegram_workflow()
