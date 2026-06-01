import yt_dlp
import asyncio
import httpx
import base64
import urllib.parse
from app.schemas.analyze import AnalyzeResponseData, FormatDTO, MediaItemDTO
from typing import Dict, Any, List

from yt_dlp.networking.impersonate import ImpersonateTarget

# Các độ phân giải chuẩn mà các nền tảng video hỗ trợ
STANDARD_RESOLUTIONS = {2160, 1440, 1080, 720, 480, 360, 240, 144}

def convert_json_to_netscape(json_path: str, netscape_path: str) -> bool:
    import json
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        if not isinstance(cookies, list):
            return False
        with open(netscape_path, 'w', encoding='utf-8') as f:
            f.write("# Netscape HTTP Cookie File\n\n")
            for c in cookies:
                domain = c.get('domain', '')
                flag = "TRUE" if domain.startswith('.') else "FALSE"
                path = c.get('path', '/')
                secure = "TRUE" if c.get('secure', False) else "FALSE"
                expiration = int(c.get('expirationDate', 0)) if c.get('expirationDate') is not None else 0
                name = c.get('name', '')
                value = c.get('value', '')
                f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}\n")
        return True
    except Exception:
        return False

def get_cookies_file_path() -> str:
    import os
    possible_paths = [
        os.path.abspath("cookies.txt"),
        os.path.abspath("backend/cookies.txt"),
        os.path.abspath("cookies.json"),
        os.path.abspath("backend/cookies.json"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read(10).strip()
                if content.startswith('['):
                    # Convert JSON to Netscape format
                    converted_path = os.path.join(os.path.dirname(path), "cookies_converted.txt")
                    if convert_json_to_netscape(path, converted_path):
                        return converted_path
            except Exception:
                pass
            return path
    return None

def _extract_instagram_sync(url: str) -> AnalyzeResponseData:
    import instaloader
    import http.cookiejar
    import base64
    import re
    
    L = instaloader.Instaloader(quiet=True)
    
    cookie_path = get_cookies_file_path()
    if cookie_path:
        try:
            cj = http.cookiejar.MozillaCookieJar(cookie_path)
            cj.load()
            L.context._session.cookies = cj
        except Exception:
            pass
            
    match = re.search(r'/(?:p|reel|tv)/([^/?#&]+)', url)
    if not match:
        raise Exception("Không tìm thấy mã bài đăng Instagram hợp lệ.")
    
    shortcode = match.group(1)
    
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
    except Exception as e:
        raise Exception(f"Lỗi khi quét Instagram: {str(e)}")
        
    media_items = []
    
    def create_format(item_url: str, is_vid: bool):
        b64_url = base64.urlsafe_b64encode(item_url.encode('utf-8')).decode('utf-8').rstrip('=')
        format_id = f"direct_url:{b64_url}"
        
        if is_vid:
            return [
                FormatDTO(
                    format_id=format_id,
                    quality_label="Video (Chất lượng cao)",
                    type="video",
                    has_audio=True,
                    has_video=True,
                    video_codec="auto",
                    audio_codec="auto",
                    estimated_size_bytes=None
                )
            ]
        else:
            return [
                FormatDTO(
                    format_id=format_id,
                    quality_label="Ảnh (Chất lượng cao)",
                    type="image",
                    has_audio=False,
                    has_video=False,
                    video_codec="none",
                    audio_codec="none",
                    estimated_size_bytes=None
                )
            ]

    def get_proxied_thumb(url: str) -> str:
        if not url: return None
        b64_url = base64.urlsafe_b64encode(url.encode('utf-8')).decode('utf-8').rstrip('=')
        return f"/api/v1/proxy-image?url=base64:{b64_url}"

    if post.typename == 'GraphSidecar':
        for idx, node in enumerate(post.get_sidecar_nodes()):
            item_url = node.video_url if node.is_video else node.display_url
            media_items.append(MediaItemDTO(
                index=idx + 1,
                thumbnail_url=get_proxied_thumb(node.display_url),
                is_video=node.is_video,
                formats=create_format(item_url, node.is_video)
            ))
    else:
        item_url = post.video_url if post.is_video else post.url
        media_items.append(MediaItemDTO(
            index=1,
            thumbnail_url=get_proxied_thumb(post.url),
            is_video=post.is_video,
            formats=create_format(item_url, post.is_video)
        ))
        
    return AnalyzeResponseData(
        title=f"Post by {post.owner_username}",
        author_name=post.owner_username,
        author_avatar=None,
        thumbnail_url=get_proxied_thumb(post.url),
        duration_seconds=None,
        formats=[],
        media_items=media_items
    )

async def _extract_tiktok_tikwm_async(url: str) -> AnalyzeResponseData:
    api_url = f"https://www.tikwm.com/api/?url={urllib.parse.quote(url)}"
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(api_url)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            raise Exception(f"Lỗi khi kết nối với máy chủ tải TikTok: {str(e)}")
            
    if result.get("code") != 0 or not result.get("data"):
        raise Exception("Không thể trích xuất dữ liệu từ link TikTok này. Bài viết có thể bị xóa hoặc giới hạn quyền riêng tư.")
        
    data = result["data"]
    title = data.get("title", "TikTok Video")
    author = data.get("author", {}).get("nickname", "Unknown")
    
    media_items = []
    
    def get_proxied_thumb(img_url: str) -> str:
        if not img_url: return None
        b64_url = base64.urlsafe_b64encode(img_url.encode('utf-8')).decode('utf-8').rstrip('=')
        return f"/api/v1/proxy-image?url=base64:{b64_url}"
    
    def create_direct_format(item_url: str, is_vid: bool):
        b64_url = base64.urlsafe_b64encode(item_url.encode('utf-8')).decode('utf-8').rstrip('=')
        format_id = f"direct_url:{b64_url}"
        
        if is_vid:
            return [
                FormatDTO(
                    format_id=format_id,
                    quality_label="Video (Không Logo)",
                    type="video",
                    has_audio=True,
                    has_video=True,
                    video_codec="auto",
                    audio_codec="auto",
                    estimated_size_bytes=None
                )
            ]
        else:
            return [
                FormatDTO(
                    format_id=format_id,
                    quality_label="Ảnh (Chất lượng cao)",
                    type="image",
                    has_audio=False,
                    has_video=False,
                    video_codec="none",
                    audio_codec="none",
                    estimated_size_bytes=None
                )
            ]
            
    # Check if it's an image carousel
    images = data.get("images")
    if images and len(images) > 0:
        for idx, img_url in enumerate(images):
            media_items.append(MediaItemDTO(
                index=idx + 1,
                thumbnail_url=get_proxied_thumb(img_url),
                is_video=False,
                formats=create_direct_format(img_url, False)
            ))
        main_thumbnail = images[0]
    else:
        # It's a single video
        video_url = data.get("play")
        main_thumbnail = data.get("cover")
        
        if video_url:
            media_items.append(MediaItemDTO(
                index=1,
                thumbnail_url=get_proxied_thumb(main_thumbnail),
                is_video=True,
                formats=create_direct_format(video_url, True)
            ))
            
    return AnalyzeResponseData(
        title=title,
        author_name=author,
        author_avatar=get_proxied_thumb(data.get("author", {}).get("avatar")),
        thumbnail_url=get_proxied_thumb(main_thumbnail),
        duration_seconds=data.get("duration", 0),
        formats=[],
        media_items=media_items
    )


def _extract_metadata_sync(url: str) -> Dict[str, Any]:
    import os
    import json
    from app.services.platform_detector import detect_platform

    try:
        platform = detect_platform(url)
    except Exception:
        platform = "unknown"

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'ignore_no_formats_error': True,
        # Cấu hình đầy đủ JavaScript runtime và giải quyết các giới hạn chặn để lấy đầy đủ độ phân giải (1080p, 720p,...)
        'js_runtimes': {'node': {}},
        'remote_components': ['ejs:github'],
        'extractor_args': {
            'youtube': {
                'player_client': ['default', '-tv', 'web_safari', 'web_embedded']
            }
        },
    }
    
    # TikTok often blocks impersonated clients, so we only impersonate Chrome for YouTube/others
    if platform != "tiktok":
        ydl_opts['impersonate'] = ImpersonateTarget.from_str('chrome')
    
    cookiefile = get_cookies_file_path()
    if cookiefile:
        ydl_opts['cookiefile'] = cookiefile
        
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

def _normalize_height(height: int) -> int:
    """Map raw height value to nearest standard resolution.
    
    YouTube/TikTok sometimes return non-standard heights like 144 or 1080.
    This maps them to the closest standard resolution.
    """
    if height <= 0:
        return 0
    # Find the closest standard resolution
    closest = min(STANDARD_RESOLUTIONS, key=lambda r: abs(r - height))
    # Only snap if within 15% tolerance (e.g., 134 -> 144, but 200 stays 200)
    if abs(closest - height) / closest <= 0.15:
        return closest
    return height

def _get_thumbnail(data: Dict[str, Any]) -> str:
    if data.get('thumbnail'):
        return data['thumbnail']
    thumbnails = data.get('thumbnails', [])
    if thumbnails:
        return thumbnails[-1].get('url')
    return data.get('url')

def _extract_formats_from_info(info: Dict[str, Any], is_video_post: bool = True) -> List[FormatDTO]:
    resolutions = set()
    formats = []
    
    # Analyze video formats
    has_video_stream = False
    for f in info.get("formats", []):
        h = f.get("height")
        vcodec = f.get("vcodec", "none")
        if h and h > 0 and vcodec != "none":
            has_video_stream = True
            normalized = _normalize_height(h)
            resolutions.add(normalized)
            
    # Add Video formats
    for res in sorted(list(resolutions), reverse=True):
        formats.append(FormatDTO(
            format_id=f"bestvideo[height<={res}]+bestaudio[ext=m4a]/bestvideo[height<={res}]+bestaudio/best[vcodec*=h264]/best[vcodec*=avc1]/best",
            quality_label=f"{res}p",
            type="video",
            has_audio=True,
            has_video=True,
            video_codec="auto",
            audio_codec="auto",
            estimated_size_bytes=None
        ))
        
    if has_video_stream or is_video_post:
        # Add Audio only format
        formats.append(FormatDTO(
            format_id="bestaudio/best",
            quality_label="Chỉ Âm thanh (MP3)",
            type="audio",
            has_audio=True,
            has_video=False,
            video_codec="none",
            audio_codec="auto",
            estimated_size_bytes=None
        ))
        # Add Thumbnail format for videos
        formats.append(FormatDTO(
            format_id="custom_image_thumbnail",
            quality_label="Ảnh bìa",
            type="image",
            has_audio=False,
            has_video=False,
            video_codec="none",
            audio_codec="none",
            estimated_size_bytes=None
        ))
    else:
        # Pure Image post
        formats.append(FormatDTO(
            format_id="best",
            quality_label="Ảnh (Chất lượng cao)",
            type="image",
            has_audio=False,
            has_video=False,
            video_codec="none",
            audio_codec="none",
            estimated_size_bytes=None
        ))
        
    return formats

async def extract_metadata(url: str) -> AnalyzeResponseData:
    """
    Run extraction in a separate thread to prevent blocking the async event loop.
    """
    from app.services.platform_detector import detect_platform
    try:
        platform = detect_platform(url)
    except ValueError:
        platform = "unknown"
        
    if platform == "instagram":
        return await asyncio.to_thread(_extract_instagram_sync, url)
        
    if platform == "tiktok":
        try:
            return await _extract_tiktok_tikwm_async(url)
        except Exception as e:
            print(f"Custom TikTok API failed: {e}. Falling back to yt-dlp.")
            pass


    try:
        info = await asyncio.to_thread(_extract_metadata_sync, url)
        
        media_items = []
        is_playlist = info.get('_type') == 'playlist'
        entries = info.get('entries', [])
        
        if is_playlist and entries:
            # Deduplicate entries (yt-dlp instagram extractor sometimes returns duplicates)
            seen = set()
            unique_entries = []
            for entry in entries:
                # Use id and url as unique key. If url is None, fallback to title or thumbnail
                entry_url = entry.get('url') or entry.get('thumbnail') or entry.get('title')
                key = (entry.get('id'), entry_url)
                if key not in seen:
                    seen.add(key)
                    unique_entries.append(entry)
            
            entries = unique_entries
            
            for idx, entry in enumerate(entries):
                # Check if entry is video or image (vcodec handling is tricky for IG, but generally we can check duration or formats)
                entry_is_video = entry.get('duration') is not None or any(f.get('vcodec') != 'none' for f in entry.get('formats', []))
                entry_formats = _extract_formats_from_info(entry, is_video_post=entry_is_video)
                
                media_items.append(MediaItemDTO(
                    index=idx + 1,
                    thumbnail_url=_get_thumbnail(entry),
                    is_video=entry_is_video,
                    formats=entry_formats
                ))
                
            # Top-level formats can be empty if it's a carousel, or we can provide a fallback
            formats = []
        else:
            # Single item
            is_video = info.get('duration') is not None or any(f.get('vcodec') != 'none' for f in info.get('formats', []))
            formats = _extract_formats_from_info(info, is_video_post=is_video)

        return AnalyzeResponseData(
            title=info.get("title", "Unknown Title"),
            author_name=info.get("uploader"),
            author_avatar=None,
            thumbnail_url=_get_thumbnail(info),
            duration_seconds=info.get("duration"),
            formats=formats,
            media_items=media_items
        )
    except Exception as e:
        raise Exception(f"YT-DLP Error: {str(e)}")
