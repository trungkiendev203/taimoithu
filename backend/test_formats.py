import asyncio
import yt_dlp
from typing import Dict, Any

from app.services.ytdlp_service import get_base_ydl_opts, execute_with_fallback

def run():
    url = "https://www.bilibili.com/video/BV1Tf7k6yEiU/"
    print(f"Testing URL: {url}")
    
    base_opts = get_base_ydl_opts("bilibili")
    base_opts['extract_flat'] = False
    
    info, _ = execute_with_fallback(url, "bilibili", base_opts, download=False)
    
    formats = info.get("formats", [])
    print(f"\nTotal formats found: {len(formats)}")
    print("-" * 80)
    print(f"{'format_id':<30} | {'ext':<5} | {'resolution':<12} | {'vcodec':<15} | {'acodec':<15}")
    print("-" * 80)
    
    has_720_or_1080 = False
    
    for f in formats:
        fid = str(f.get("format_id", ""))
        ext = str(f.get("ext", ""))
        w = f.get("width", "0")
        h = f.get("height", "0")
        res = f"{w}x{h}" if w and h else f.get("resolution", "")
        vc = str(f.get("vcodec", "none"))
        ac = str(f.get("acodec", "none"))
        
        if h and h != "none" and str(h).isdigit():
            height = int(h)
            if height >= 720:
                has_720_or_1080 = True
                
        print(f"{fid:<30} | {ext:<5} | {res:<12} | {vc:<15} | {ac:<15}")
        
    print("-" * 80)
    if has_720_or_1080:
        print("=> yt-dlp NHÌN THẤY 720p/1080p!")
    else:
        print("=> yt-dlp KHÔNG NHÌN THẤY 720p/1080p (Thường do Bilibili giới hạn nếu không có cookie VIP/đăng nhập).")

if __name__ == "__main__":
    run()
