import re
from urllib.parse import urlparse

# Mảng regex kiểm tra private IPs
PRIVATE_IP_REGEX = [
    re.compile(r"^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$"),
    re.compile(r"^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$"),
    re.compile(r"^192\.168\.\d{1,3}\.\d{1,3}$"),
    re.compile(r"^172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}$"),
    re.compile(r"^0\.0\.0\.0$"),
]

def is_safe_url(url: str) -> bool:
    """
    Validate an input URL for basic security (prevent simple SSRF logic in Phase 1).
    Does not do full DNS resolution yet (stub for MVP).
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return False
        
    if parsed.scheme not in ["http", "https"]:
        return False
        
    hostname = parsed.hostname
    if not hostname or "." not in hostname:
        return False
        
    # Block explicitly localhost
    if hostname.lower() in ["localhost", "127.0.0.1", "0.0.0.0", "::1"]:
        return False
        
    # Check IP patterns
    for regex in PRIVATE_IP_REGEX:
        if regex.match(hostname):
            return False
            
    return True
