"""TikTok video metadata extraction using TikWM API."""
import urllib.parse
import httpx
from app.schemas.analyze import AnalyzeResponseData, MediaItemDTO
from app.services.helpers import get_proxied_thumb, create_direct_format


async def extract_tiktok_tikwm(url: str) -> AnalyzeResponseData:
    """Extract TikTok metadata via tikwm.com API."""
    api_url = f"https://www.tikwm.com/api/?url={urllib.parse.quote(url)}"

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(api_url)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            raise Exception(f"Lỗi khi kết nối với máy chủ tải TikTok: {str(e)}")

    if result.get("code") != 0 or not result.get("data"):
        raise Exception(
            "Không thể trích xuất dữ liệu từ link TikTok này. "
            "Bài viết có thể bị xóa hoặc giới hạn quyền riêng tư."
        )

    data = result["data"]
    title = data.get("title", "TikTok Video")
    author = data.get("author", {}).get("nickname", "Unknown")

    media_items = []

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
        # Single video
        video_url = data.get("play")
        main_thumbnail = data.get("cover")
        if video_url:
            media_items.append(MediaItemDTO(
                index=1,
                thumbnail_url=get_proxied_thumb(main_thumbnail),
                is_video=True,
                formats=create_direct_format(video_url, True, "Video (Không Logo)")
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
