"""Shared helper functions for all platform extractors."""
import base64
import json
import os
from typing import List, Optional
from app.schemas.analyze import FormatDTO
from app.core.config import settings


def get_proxied_thumb(url: str) -> Optional[str]:
    """Generate a proxied thumbnail URL to bypass CORS."""
    if not url:
        return None
    b64_url = base64.urlsafe_b64encode(url.encode('utf-8')).decode('utf-8').rstrip('=')
    return f"/api/v1/proxy-image?url=base64:{b64_url}"


def create_direct_format(
    item_url: str, is_vid: bool,
    video_label: str = "Video (Chất lượng cao)"
) -> List[FormatDTO]:
    """Create a FormatDTO list for a direct URL download."""
    b64_url = base64.urlsafe_b64encode(
        item_url.encode('utf-8')
    ).decode('utf-8').rstrip('=')
    format_id = f"direct_url:{b64_url}"

    if is_vid:
        return [FormatDTO(
            format_id=format_id, quality_label=video_label,
            type="video", has_audio=True, has_video=True,
            video_codec="auto", audio_codec="auto",
            estimated_size_bytes=None
        )]
    return [FormatDTO(
        format_id=format_id, quality_label="Ảnh (Chất lượng cao)",
        type="image", has_audio=False, has_video=False,
        video_codec="none", audio_codec="none",
        estimated_size_bytes=None
    )]


def convert_json_to_netscape(json_path: str, netscape_path: str) -> bool:
    """Convert JSON cookie file to Netscape format for yt-dlp."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        if not isinstance(cookies, list):
            return False
        with open(netscape_path, 'w', encoding='utf-8') as f:
            f.write("# Netscape HTTP Cookie File\n\n")
            for c in cookies:
                name = c.get('name', '')
                if not name:
                    continue  # FIX: Skip cookies with empty name
                domain = c.get('domain', '')
                flag = "TRUE" if domain.startswith('.') else "FALSE"
                path = c.get('path', '/')
                secure = "TRUE" if c.get('secure', False) else "FALSE"
                exp = int(c.get('expirationDate', 0)) if c.get('expirationDate') is not None else 0
                value = c.get('value', '')
                f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{exp}\t{name}\t{value}\n")
        return True
    except Exception:
        return False


def get_cookies_file_path(return_json: bool = False, prefix: str = "cookies") -> Optional[str]:
    """Find and return the path to a valid cookies file.

    Searches relative to CWD. Auto-converts JSON to Netscape if needed.
    """
    possible_paths = []
    if prefix == "cookies" and settings.YTDLP_COOKIES_FILE:
        possible_paths.append(os.path.abspath(settings.YTDLP_COOKIES_FILE))
        
    possible_paths.extend([
        os.path.abspath(f"{prefix}.txt"),
        os.path.abspath(f"backend/{prefix}.txt"),
        os.path.abspath(f"{prefix}.json"),
        os.path.abspath(f"backend/{prefix}.json"),
    ])
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read(10).strip()
                if content.startswith('['):
                    if return_json:
                        return path
                    converted = os.path.join(os.path.dirname(path), f"{prefix}_converted.txt")
                    if convert_json_to_netscape(path, converted):
                        return converted
            except Exception:
                pass
            return path
            
    return None


def load_playwright_cookies() -> list:
    """Load cookies from JSON file for Playwright, filtering invalid entries.

    Uses the same get_cookies_file_path() to ensure consistency with yt-dlp.
    """
    cookie_path = get_cookies_file_path(return_json=True)
    if not cookie_path or not os.path.exists(cookie_path):
        print(f"Playwright: Cookie file not found")
        return []

    try:
        with open(cookie_path, 'r', encoding='utf-8') as f:
            content = f.read(10).strip()
            f.seek(0)
            if not content.startswith('['):
                return []  # Not JSON format, skip
            raw_cookies = json.load(f)
    except Exception as e:
        print(f"Playwright cookie load error: {e}")
        return []

    pw_cookies = []
    for c in raw_cookies:
        name = c.get("name", "")
        domain = c.get("domain", "")
        if not name or not domain:
            continue  # FIX: Skip cookies with empty name/domain
        pw_cookies.append({
            "name": name,
            "value": c.get("value", ""),
            "domain": domain,
            "path": c.get("path", "/"),
        })
    return pw_cookies


def detect_referer_for_cdn(cdn_url: str) -> str:
    """Guess appropriate Referer header based on CDN URL domain."""
    if not cdn_url:
        return ""
    lower = cdn_url.lower()
    if any(d in lower for d in ['douyinpic', 'byteimg', 'pstatp', 'douyin']):
        return "https://www.douyin.com/"
    if any(d in lower for d in ['tiktokcdn', 'muscdn', 'tiktok']):
        return "https://www.tiktok.com/"
    if any(d in lower for d in ['cdninstagram', 'fbcdn', 'instagram']):
        return "https://www.instagram.com/"
    if any(d in lower for d in ['youtube', 'googlevideo', 'ytimg']):
        return "https://www.youtube.com/"
    if any(d in lower for d in ['bilivideo', 'hdslb', 'bilibili']):
        return "https://www.bilibili.com/"
    return ""


# Map platform name → Referer URL (used by download tasks)
PLATFORM_REFERER_MAP = {
    "douyin": "https://www.douyin.com/",
    "tiktok": "https://www.tiktok.com/",
    "instagram": "https://www.instagram.com/",
    "youtube": "https://www.youtube.com/",
    "bilibili": "https://www.bilibili.com/",
    "facebook": "https://www.facebook.com/",
    "twitter": "https://x.com/",
}
