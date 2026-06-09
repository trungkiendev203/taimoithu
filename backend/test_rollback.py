import os
import shutil
from unittest.mock import MagicMock
os.environ["TELEGRAM_BOT_TOKEN"] = "123456:mock_token"
from app.services.telegram_bot import handle_cookie_document, rollback_cookie, get_cookies_file_path

def test_rollback():
    print("\n--- Rollback Real Test ---")
    cookie_path = "backend/cookies.txt" if os.path.exists("backend") else "cookies.txt"
    backup_dir = "backend/backups" if os.path.exists("backend") else "backups"
    
    # Dọn dẹp
    if os.path.exists(cookie_path): os.remove(cookie_path)
    if os.path.exists(backup_dir): shutil.rmtree(backup_dir)
    
    import app.services.telegram_bot as tb
    tb.ADMIN_ID = "12345"
    tb.bot = MagicMock()
    tb.bot.reply_to = lambda msg, text: print(f"[Bot]: {text}")
    
    # 1. Upload cookie A
    print("\n[User]: Upload Cookie A")
    msg_a = MagicMock()
    msg_a.from_user.id = 12345
    msg_a.document.file_name = "cookies.txt"
    msg_a.document.file_size = 500
    
    tb.bot.get_file = lambda f_id: MagicMock()
    tb.bot.download_file = lambda path: b"COOKIE_A_CONTENT"
    handle_cookie_document(msg_a)
    
    with open(cookie_path, "rb") as f:
        print(f"Current Cookie Content: {f.read()}")
        
    # Wait a bit to ensure timestamp difference
    import time
    time.sleep(2)
    
    # 2. Upload cookie B
    print("\n[User]: Upload Cookie B")
    msg_b = MagicMock()
    msg_b.from_user.id = 12345
    msg_b.document.file_name = "cookies.txt"
    msg_b.document.file_size = 500
    
    tb.bot.download_file = lambda path: b"COOKIE_B_CONTENT"
    handle_cookie_document(msg_b)
    
    with open(cookie_path, "rb") as f:
        print(f"Current Cookie Content: {f.read()}")
        
    print(f"Backups available: {os.listdir(backup_dir)}")
    
    # 3. Rollback
    print("\n[User]: /rollback_cookie")
    rollback_cookie(msg_a)
    
    with open(cookie_path, "rb") as f:
        print(f"Current Cookie Content After Rollback: {f.read()}")

if __name__ == "__main__":
    test_rollback()
