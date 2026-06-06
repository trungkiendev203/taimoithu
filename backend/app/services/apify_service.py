import httpx
from app.schemas.analyze import AnalyzeResponseData, MediaItemDTO
from app.services.helpers import get_proxied_thumb, create_direct_format
from app.core.config import settings
import urllib.parse
import json

async def extract_douyin_apify(url: str) -> AnalyzeResponseData:
    """Extract metadata using Apify Douyin Video Downloader Actor."""
    if not settings.APIFY_TOKEN:
        raise Exception("APIFY_TOKEN chưa được cấu hình trong .env")

    # The Actor ID for easyapi/douyin-video-downloader
    actor_id = "easyapi~douyin-video-downloader"
    api_url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items?token={settings.APIFY_TOKEN}"
    
    # Chuẩn bị payload dựa trên tài liệu phổ biến của Apify
    payload = {
        "videoURLs": [url]
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(api_url, json=payload)
            response.raise_for_status()
            results = response.json()
        except Exception as e:
            # Bắt lỗi JSON parse hoặc lỗi HTTP
            if hasattr(e, 'response') and e.response:
                error_body = e.response.text
                raise Exception(f"Lỗi khi gọi Apify: {e.response.status_code} - {error_body}")
            raise Exception(f"Lỗi khi kết nối với Apify: {type(e).__name__}: {str(e)}")

    if not results or len(results) == 0:
        raise Exception("Apify trả về dữ liệu rỗng. Có thể do Douyin chặn hoặc URL không hợp lệ.")

    # Apify trả về mảng kết quả
    item = results[0]
    data = item.get("result", item) # fallback nếu nằm ngay ngoài

    if data.get("error"):
        raise Exception(f"Apify trả về lỗi: {data.get('message', 'Không rõ')}")

    title = data.get("title") or data.get("desc") or "Douyin Video"
    author = data.get("author") or "Unknown"
    author_avatar = data.get("avatar") # Có thể null
    
    # Thumbnail
    main_thumbnail = data.get("thumbnail") or data.get("cover")

    media_items = []
    medias = data.get("medias", [])
    
    # Lọc ra các video no watermark
    videos = [m for m in medias if m.get("type") == "video" and "no_watermark" in m.get("quality", "")]
    # Hoặc lấy video thường nếu không có no_watermark
    if not videos:
        videos = [m for m in medias if m.get("type") == "video"]
        
    images = [m for m in medias if m.get("type") == "image"]

    if images and len(images) > 0:
        for idx, img in enumerate(images):
            img_url = img.get("url")
            if img_url:
                media_items.append(MediaItemDTO(
                    index=idx + 1,
                    thumbnail_url=get_proxied_thumb(img_url),
                    is_video=False,
                    formats=create_direct_format(img_url, False)
                ))
    elif videos:
        # Lấy video nét nhất
        best_video = videos[0]
        video_url = best_video.get("url")
        if video_url:
            media_items.append(MediaItemDTO(
                index=1,
                thumbnail_url=get_proxied_thumb(main_thumbnail),
                is_video=True,
                formats=create_direct_format(video_url, True)
            ))

    duration_sec = data.get("duration", 0)
    if duration_sec > 10000:
        duration_sec = duration_sec // 1000

    return AnalyzeResponseData(
        title=title,
        author_name=author,
        author_avatar=get_proxied_thumb(author_avatar),
        thumbnail_url=get_proxied_thumb(main_thumbnail),
        duration_seconds=duration_sec,
        formats=[],
        media_items=media_items
    )
