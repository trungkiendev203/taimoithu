import time
import os
import shutil
from app.services.ytdlp_service import execute_with_fallback, get_base_ydl_opts

BILI_URL = "https://www.bilibili.com/video/BV1xx411c7mD"

def test_scenario(scenario_name, cookie_content):
    print(f"\n--- Testing Scenario: {scenario_name} ---")
    cookie_path = "backend/cookies.txt" if os.path.exists("backend") else "cookies.txt"
    converted_path = "backend/cookies_converted.txt" if os.path.exists("backend") else "cookies_converted.txt"
    
    if cookie_content is None:
        if os.path.exists(cookie_path): os.remove(cookie_path)
        if os.path.exists(converted_path): os.remove(converted_path)
    else:
        with open(cookie_path, "w") as f:
            f.write(cookie_content)
            
    start_time = time.time()
    base_opts = get_base_ydl_opts("bilibili")
    try:
        info, _ = execute_with_fallback(BILI_URL, "bilibili", base_opts, download=False)
        formats = [f.get('height') for f in info.get('formats', []) if f.get('height')]
        max_res = max(formats) if formats else None
        print(f"Result: SUCCESS")
        print(f"Max Resolution: {max_res}p")
    except Exception as e:
        print(f"Result: ERROR ({e})")
        
    duration = time.time() - start_time
    print(f"Time Taken: {duration:.2f} seconds")

if __name__ == "__main__":
    # a) Không cookie
    test_scenario("Không có cookie", None)
    
    # c) Cookie hết hạn/không hợp lệ
    # Một cookie giả mạo sẽ khiến yt-dlp cố dùng nhưng bị lỗi hoặc không có tác dụng
    fake_cookie = """# Netscape HTTP Cookie File
.bilibili.com	TRUE	/	FALSE	1799999999	SESSDATA	fake_invalid_session_data
"""
    test_scenario("Expired", fake_cookie)
    test_scenario("Valid_Simulated", fake_cookie)
