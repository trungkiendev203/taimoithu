"""Evil0ctal Douyin/TikTok Download API integration."""
import urllib.parse
import httpx
from app.schemas.analyze import AnalyzeResponseData, MediaItemDTO
from app.services.helpers import get_proxied_thumb, create_direct_format
from app.core.config import settings


async def extract_evil0ctal(url: str, platform: str) -> AnalyzeResponseData:
    """Extract metadata via Evil0ctal API (Docker service or configurable URL)."""
    base_url = settings.EVIL0CTAL_URL
    api_url = f"{base_url}/api/hybrid/video_data?url={urllib.parse.quote(url)}"

    async with httpx.AsyncClient(timeout=45.0) as client:
        try:
            response = await client.get(api_url)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            raise Exception(
                f"Lỗi khi kết nối với máy chủ Evil0ctal: {type(e).__name__}: {str(e)}"
            )

    if result.get("code") != 200 or not result.get("data"):
        raise Exception(
            f"Evil0ctal trả về lỗi: {result.get('message', 'Unknown error')}"
        )

    data = result["data"]
    print("EVIL0CTAL RAW DATA:", data)
    title = data.get("desc", f"{platform.capitalize()} Video")
    author = data.get("author", {}).get("nickname", "Unknown")

    media_items = []

    # Check if it's an image carousel
    duration = 0
    if "video" in data:
        # duration is often in ms (e.g. 461967 -> 461.967s) or seconds. 
        raw_duration = data["video"].get("duration", 0)
        duration = int(raw_duration / 1000) if raw_duration > 10000 else int(raw_duration)
    elif "video_data" in data:
        duration = data["video_data"].get("duration", 0)
        
    image_data = data.get("image_data", {})
    images = (
        image_data.get("no_watermark_image_list", [])
        if isinstance(image_data, dict)
        else []
    )

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
        # Single video
        video_data = data.get("video", {})
        play_addr = video_data.get("play_addr", {})
        video_url = None
        if play_addr and "url_list" in play_addr and len(play_addr["url_list"]) > 0:
            video_url = play_addr["url_list"][0]

        # Fallback to old format just in case
        if not video_url:
            old_video_data = data.get("video_data", {})
            video_url = (
                old_video_data.get("nwm_video_url_HQ")
                or old_video_data.get("nwm_video_url")
            )

        cover_data = video_data.get("cover", {})
        cover_list = cover_data.get("url_list", []) if cover_data else []
        if not cover_list:
            cover_list = data.get("cover_data", {}).get("cover", {}).get("url_list", [None])
            
        main_thumbnail = cover_list[0] if cover_list else None

        if video_url:
            media_items.append(MediaItemDTO(
                index=1,
                thumbnail_url=get_proxied_thumb(main_thumbnail),
                is_video=True,
                formats=create_direct_format(video_url, True)
            ))

    author_avatar = None
    author_info = data.get("author", {})
    if isinstance(author_info, dict):
        avatar_dict = author_info.get("avatar_thumb", {}) or author_info.get("avatar_medium", {})
        if isinstance(avatar_dict, dict) and "url_list" in avatar_dict and avatar_dict["url_list"]:
            author_avatar = avatar_dict["url_list"][0]

    return AnalyzeResponseData(
        title=title,
        author_name=author,
        author_avatar=get_proxied_thumb(author_avatar) if author_avatar else None,
        thumbnail_url=get_proxied_thumb(main_thumbnail),
        duration_seconds=duration,
        formats=[],
        media_items=media_items
    )
