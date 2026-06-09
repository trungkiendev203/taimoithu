from urllib.parse import urlparse

SUPPORTED_DOMAINS = [
    "youtube.com", "youtu.be",
    "tiktok.com", "douyin.com", "iesdouyin.com",
    "bilibili.com", "bilibili.tv",
    "facebook.com", "fb.watch", "fb.com",
    "instagram.com",
    "twitter.com", "x.com",
    "soundcloud.com", "on.soundcloud.com"
]

def detect_platform(url: str) -> str:
    """
    Detect platform from URL hostname.
    Raises ValueError if unsupported.
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname.lower() if parsed.hostname else ""
    except Exception:
        raise ValueError("UNSUPPORTED_PLATFORM")
        
    for domain in SUPPORTED_DOMAINS:
        if domain in hostname:
            if "youtube" in domain or "youtu.be" in domain:
                return "youtube"
            if "tiktok" in domain:
                return "tiktok"
            if "douyin" in domain:
                return "douyin"
            if "bilibili" in domain:
                return "bilibili"
            if "facebook" in domain or "fb." in domain:
                return "facebook"
            if "instagram" in domain:
                return "instagram"
            if "twitter" in domain or "x.com" in domain:
                return "twitter"
            if "soundcloud" in domain:
                return "soundcloud"
                
    raise ValueError("UNSUPPORTED_PLATFORM")
