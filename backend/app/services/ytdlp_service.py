"""Core yt-dlp extraction and main extract_metadata router.

This module handles:
- yt-dlp based metadata extraction (YouTube, Facebook, Twitter, etc.)
- Format normalization and resolution mapping
- Main routing logic that delegates to platform-specific extractors
"""
import asyncio
import re
from typing import Dict, Any, List
import yt_dlp

from app.schemas.analyze import AnalyzeResponseData, FormatDTO, MediaItemDTO
from app.services.helpers import get_cookies_file_path, get_proxied_thumb
from app.services.platform_detector import detect_platform
from app.core.exceptions import AppException
from app.core.logger import logger

# Các độ phân giải chuẩn mà các nền tảng video hỗ trợ
STANDARD_RESOLUTIONS = {2160, 1440, 1080, 720, 480, 360, 240, 144}


def _normalize_height(height: int) -> int:
    """Map raw height value to nearest standard resolution.

    YouTube/TikTok sometimes return non-standard heights like 134 or 1078.
    This maps them to the closest standard resolution within 15% tolerance.
    """
    if height <= 0:
        return 0
    closest = min(STANDARD_RESOLUTIONS, key=lambda r: abs(r - height))
    if abs(closest - height) / closest <= 0.15:
        return closest
    return height


def _get_thumbnail(data: Dict[str, Any]) -> str:
    """Extract thumbnail URL from yt-dlp info dict."""
    if data.get('thumbnail'):
        return data['thumbnail']
    thumbnails = data.get('thumbnails', [])
    if thumbnails:
        return thumbnails[-1].get('url')
    return data.get('url')


def _extract_formats_from_info(
    info: Dict[str, Any], is_video_post: bool = True
) -> List[FormatDTO]:
    """Build FormatDTO list from yt-dlp format info."""
    resolutions = set()
    formats = []

    has_video_stream = False
    for f in info.get("formats", []):
        h = f.get("height")
        vcodec = f.get("vcodec", "none")
        if h and h > 0 and vcodec != "none":
            has_video_stream = True
            normalized = _normalize_height(h)
            resolutions.add(normalized)

    # Video formats sorted by resolution (descending)
    for res in sorted(list(resolutions), reverse=True):
        fmt_id = (
            f"bestvideo[height<={res}]+bestaudio[ext=m4a]/"
            f"bestvideo[height<={res}]+bestaudio/"
            f"best[vcodec*=h264]/best[vcodec*=avc1]/best"
        )
        formats.append(FormatDTO(
            format_id=fmt_id, quality_label=f"{res}p",
            type="video", has_audio=True, has_video=True,
            video_codec="auto", audio_codec="auto",
            estimated_size_bytes=None
        ))

    if has_video_stream or is_video_post:
        # Audio only
        formats.append(FormatDTO(
            format_id="bestaudio/best",
            quality_label="Chỉ Âm thanh (MP3)",
            type="audio", has_audio=True, has_video=False,
            video_codec="none", audio_codec="auto",
            estimated_size_bytes=None
        ))
        # Thumbnail
        formats.append(FormatDTO(
            format_id="custom_image_thumbnail",
            quality_label="Ảnh bìa",
            type="image", has_audio=False, has_video=False,
            video_codec="none", audio_codec="none",
            estimated_size_bytes=None
        ))
    else:
        formats.append(FormatDTO(
            format_id="best",
            quality_label="Ảnh (Chất lượng cao)",
            type="image", has_audio=False, has_video=False,
            video_codec="none", audio_codec="none",
            estimated_size_bytes=None
        ))

    return formats


def get_base_ydl_opts(platform: str) -> dict:
    """Trả về cấu hình yt-dlp mặc định dùng cho mọi nền tảng."""
    opts = {
        'quiet': True,
        'no_warnings': True,
        'ignore_no_formats_error': True,
        'js_runtimes': {'node': {}},
        'remote_components': ['ejs:github'],
    }
    
    if platform == 'youtube':
        opts['extractor_args'] = {
            'youtube': {'player_client': ['default', '-tv', 'web_safari', 'web_embedded']}
        }
        opts['noplaylist'] = True
    elif platform == 'douyin':
        pass
    elif platform == 'bilibili':
        opts['http_headers'] = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.bilibili.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        
    return opts

def execute_with_fallback(url: str, platform: str, base_opts: dict, download: bool = False) -> tuple[Dict[str, Any], str | None]:
    """Execute yt-dlp extraction with fallback strategies:
    1. Lần 1: Cấu hình chuẩn
    2. Lần 2: Retry với cookies nếu có
    """
    cookiefile = get_cookies_file_path()
    strategies = []
    
    # Lần 1: Cấu hình chuẩn
    opts_1 = dict(base_opts)
    
    # Lần 2: Retry với cookies nếu có
    if cookiefile:
        opts_2 = dict(base_opts)
        opts_2['cookiefile'] = cookiefile
        
        if platform == 'bilibili':
            # Bilibili: Ưu tiên dùng cookie để lấy chất lượng cao
            strategies.append(opts_2)
            strategies.append(opts_1)
        else:
            strategies.append(opts_1)
            strategies.append(opts_2)
    else:
        strategies.append(opts_1)
        
    last_error = None
    for idx, opts in enumerate(strategies):
        logger.info(f"[YTDLP] Attempt {idx + 1} with opts: {opts}")
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=download)
                final_file = ydl.prepare_filename(info) if download else None
                return info, final_file
        except Exception as e:
            last_error = e
            logger.warning(f"[YTDLP] Attempt {idx + 1} failed: {str(e)}")
            continue
            
    raise last_error

def _extract_metadata_sync(url: str) -> Dict[str, Any]:
    """Run yt-dlp extraction synchronously (for asyncio.to_thread)."""
    logger.info(f"[EXTRACT] Bắt đầu phân tích URL gốc: {url}")
    
    try:
        platform = detect_platform(url)
    except Exception:
        platform = "unknown"

    # Normalize Douyin modal_id URLs
    if platform == "douyin":
        match = re.search(r'modal_id=(\d+)', url)
        if match:
            url = f"https://www.douyin.com/video/{match.group(1)}"
        else:
            note_match = re.search(r'/note/(\d+)', url)
            if note_match:
                url = f"https://www.douyin.com/video/{note_match.group(1)}"

    class YtdlpLogger:
        def debug(self, msg):
            pass
        def warning(self, msg):
            logger.warning(f"yt-dlp warning: {msg}")
        def error(self, msg):
            logger.error(f"yt-dlp error: {msg}")

    base_opts = get_base_ydl_opts(platform)
    base_opts['logger'] = YtdlpLogger()
    base_opts['extract_flat'] = False
    
    info, _ = execute_with_fallback(url, platform, base_opts, download=False)
    return info


async def extract_metadata(url: str) -> AnalyzeResponseData:
    """Main extraction router — delegates to platform-specific extractors.

    Falls back to yt-dlp for unsupported or failed platform extractors.
    """
    try:
        platform = detect_platform(url)
    except ValueError:
        platform = "unknown"

    # --- Instagram ---
    if platform == "instagram":
        try:
            from app.services.instagram_service import extract_instagram
            return await asyncio.to_thread(extract_instagram, url)
        except Exception as e:
            print(f"Instaloader API failed: {e}. Falling back to yt-dlp.")

    # --- TikTok ---
    if platform == "tiktok":
        try:
            from app.services.tiktok_service import extract_tiktok_tikwm
            return await extract_tiktok_tikwm(url)
        except Exception as e:
            print(f"Custom TikTok API failed: {e}. Falling back to yt-dlp.")

    # --- Douyin ---
    if platform == "douyin":
        # Normalize Douyin modal_id URLs for all extractors
        match = re.search(r'modal_id=(\d+)', url)
        if match:
            url = f"https://www.douyin.com/video/{match.group(1)}"
        else:
            note_match = re.search(r'/note/(\d+)', url)
            if note_match:
                url = f"https://www.douyin.com/video/{note_match.group(1)}"

        from app.core.config import settings
        if settings.APIFY_TOKEN:
            try:
                from app.services.apify_service import extract_douyin_apify
                return await extract_douyin_apify(url)
            except Exception as e:
                print(f"Apify API failed: {e}. Falling back to Evil0ctal.")
        try:
            from app.services.evil0ctal_service import extract_evil0ctal
            return await extract_evil0ctal(url, platform)
        except Exception as ee:
            print(f"Evil0ctal API failed: {ee}. Falling back to Playwright.")
        try:
            from app.services.douyin_service import extract_douyin_playwright
            return await extract_douyin_playwright(url)
        except Exception as pe:
            print(f"Playwright API failed: {pe}. Falling back to yt-dlp.")

    # --- Bilibili ---
    if platform == "bilibili":
        try:
            from app.services.evil0ctal_service import extract_evil0ctal
            return await extract_evil0ctal(url, platform)
        except Exception as e:
            print(f"Evil0ctal API failed: {e}. Falling back to yt-dlp.")

    # --- SoundCloud ---
    if platform == "soundcloud":
        try:
            from app.services.soundcloud_service import extract_soundcloud
            return await extract_soundcloud(url)
        except Exception as e:
            print(f"SoundCloud extraction failed: {e}. Falling back to yt-dlp.")

    # --- Fallback: yt-dlp ---
    try:
        info = await asyncio.to_thread(_extract_metadata_sync, url)

        media_items = []
        is_playlist = info.get('_type') == 'playlist'
        entries = info.get('entries', [])

        if is_playlist and entries:
            # Deduplicate entries
            seen = set()
            unique_entries = []
            for entry in entries:
                entry_url = (
                    entry.get('url') or entry.get('thumbnail') or entry.get('title')
                )
                key = (entry.get('id'), entry_url)
                if key not in seen:
                    seen.add(key)
                    unique_entries.append(entry)
            entries = unique_entries

            for idx, entry in enumerate(entries):
                entry_is_video = (
                    entry.get('duration') is not None
                    or any(f.get('vcodec') != 'none' for f in entry.get('formats', []))
                )
                entry_formats = _extract_formats_from_info(entry, is_video_post=entry_is_video)
                media_items.append(MediaItemDTO(
                    index=idx + 1,
                    thumbnail_url=get_proxied_thumb(_get_thumbnail(entry)),
                    is_video=entry_is_video,
                    formats=entry_formats
                ))
            formats = []
        else:
            is_video = (
                info.get('duration') is not None
                or any(f.get('vcodec') != 'none' for f in info.get('formats', []))
            )
            formats = _extract_formats_from_info(info, is_video_post=is_video)

        raw_dur = info.get("duration")
        duration_sec = int(float(raw_dur)) if raw_dur is not None else None

        return AnalyzeResponseData(
            title=info.get("title", "Unknown Title"),
            author_name=info.get("uploader"),
            author_avatar=None,
            thumbnail_url=get_proxied_thumb(_get_thumbnail(info)),
            duration_seconds=duration_sec,
            formats=formats,
            media_items=media_items
        )
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Extraction failed for {url}: {error_msg}")
        
        # Parse yt-dlp/instaloader/evil0ctal specific errors
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
