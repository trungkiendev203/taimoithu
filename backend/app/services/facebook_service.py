import asyncio
import httpx
import re
from typing import Any, Dict

from app.schemas.analyze import AnalyzeResponseData
from app.services.ytdlp_service import _extract_metadata_sync, _extract_formats_from_info, _get_thumbnail
from app.services.helpers import get_proxied_thumb
from app.core.exceptions import AppException
from app.core.logger import logger

async def resolve_facebook_redirect(url: str) -> str:
    """Resolve fb.watch or m.facebook.com redirects to get the real video URL."""
    if "fb.watch" not in url and "m.facebook.com" not in url:
        return url
        
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            # We use a standard user agent to avoid being blocked
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            resp = await client.get(url, headers=headers)
            final_url = str(resp.url)
            logger.info(f"[FACEBOOK] Resolved {url} -> {final_url}")
            return final_url
    except Exception as e:
        logger.warning(f"[FACEBOOK] Failed to resolve redirect for {url}: {e}")
        return url

async def extract_facebook(url: str) -> AnalyzeResponseData:
    """
    Extract metadata specifically for Facebook videos.
    Uses yt-dlp as the engine, with pre-processing for Facebook specific URLs.
    """
    # 1. Pre-process URL (resolve fb.watch / mobile URLs)
    resolved_url = await resolve_facebook_redirect(url)
    
    # 2. Extract using yt-dlp sync wrapper
    try:
        info = await asyncio.to_thread(_extract_metadata_sync, resolved_url)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Facebook extraction failed for {url}: {error_msg}")
        lower_msg = error_msg.lower()
        
        if "only available for registered users" in lower_msg or "private video" in lower_msg or "private" in lower_msg or "login to see" in lower_msg:
            raise AppException("PRIVATE_CONTENT", "Video này thuộc tài khoản riêng tư hoặc yêu cầu theo dõi. Hệ thống không thể truy cập nếu không có phiên đăng nhập hợp lệ.", status_code=400)
        elif "login" in lower_msg or "sign in" in lower_msg or "authentication" in lower_msg:
            raise AppException("LOGIN_REQUIRED", "Video này yêu cầu đăng nhập để xem.", status_code=400)
        elif "geo" in lower_msg or "country" in lower_msg or "region" in lower_msg:
            raise AppException("GEO_BLOCKED", "Video bị giới hạn ở một số quốc gia.", status_code=400)
        elif "rate-limit" in lower_msg or "too many requests" in lower_msg or "429" in lower_msg:
            raise AppException("RATE_LIMITED", "Hệ thống đang bị giới hạn lượt tải từ nền tảng này.", status_code=429)
        elif "unavailable" in lower_msg or "not found" in lower_msg or "404" in lower_msg or "deleted" in lower_msg:
            raise AppException("VIDEO_UNAVAILABLE", "Video không tồn tại hoặc đã bị xóa.", status_code=404)
        elif "network" in lower_msg or "connection" in lower_msg or "timeout" in lower_msg:
            raise AppException("NETWORK_ERROR", "Lỗi kết nối mạng khi lấy dữ liệu video.", status_code=500)
        elif "invalid url" in lower_msg or "unsupported url" in lower_msg:
            raise AppException("INVALID_URL", "Invalid video URL", status_code=400)
        else:
            raise AppException("UNKNOWN_ERROR", f"Đã xảy ra lỗi không xác định: {error_msg}", status_code=500)
        
    # 3. Format the response to map exactly to AnalyzeResponseData
    is_video = (
        info.get('duration') is not None
        or any(f.get('vcodec') != 'none' for f in info.get('formats', []))
    )
    
    formats = _extract_formats_from_info(info, is_video_post=is_video)
    
    raw_dur = info.get("duration")
    duration_sec = int(float(raw_dur)) if raw_dur is not None else None
    
    return AnalyzeResponseData(
        title=info.get("title", "Facebook Video"),
        author_name=info.get("uploader", "Facebook User"),
        author_avatar=None,
        thumbnail_url=get_proxied_thumb(_get_thumbnail(info)),
        duration_seconds=duration_sec,
        formats=formats,
        media_items=[]
    )
