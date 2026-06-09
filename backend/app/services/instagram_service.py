"""Instagram metadata extraction using Instaloader."""
import re
import base64
import http.cookiejar
import instaloader
from app.schemas.analyze import AnalyzeResponseData, FormatDTO, MediaItemDTO
from app.services.helpers import get_proxied_thumb, get_cookies_file_path


def extract_instagram(url: str) -> AnalyzeResponseData:
    """Extract Instagram post metadata (sync, run via asyncio.to_thread)."""
    L = instaloader.Instaloader(quiet=True)

    cookie_path = get_cookies_file_path(prefix="ig_cookies")
    if cookie_path:
        try:
            cj = http.cookiejar.MozillaCookieJar(cookie_path)
            cj.load()
            
            # Chỉ nạp cookie nếu thực sự có cookie của Instagram
            has_ig = any("instagram.com" in cookie.domain for cookie in cj)
            if has_ig:
                L.context._session.cookies.update(cj)
        except Exception as e:
            print(f"Instagram: Không thể nạp cookie: {e}")

    match = re.search(r'/(?:p|reel|tv)/([^/?#&]+)', url)
    if not match:
        raise Exception("Không tìm thấy mã bài đăng Instagram hợp lệ.")

    shortcode = match.group(1)

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
    except Exception as e:
        raise Exception(f"Lỗi khi quét Instagram: {str(e)}")

    media_items = []

    def _create_format(item_url: str, is_vid: bool):
        b64_url = base64.urlsafe_b64encode(
            item_url.encode('utf-8')
        ).decode('utf-8').rstrip('=')
        fmt_id = f"direct_url:{b64_url}"

        if is_vid:
            return [FormatDTO(
                format_id=fmt_id,
                quality_label="Video (Chất lượng cao)",
                type="video", has_audio=True, has_video=True,
                video_codec="auto", audio_codec="auto",
                estimated_size_bytes=None
            )]
        return [FormatDTO(
            format_id=fmt_id,
            quality_label="Ảnh (Chất lượng cao)",
            type="image", has_audio=False, has_video=False,
            video_codec="none", audio_codec="none",
            estimated_size_bytes=None
        )]

    if post.typename == 'GraphSidecar':
        for idx, node in enumerate(post.get_sidecar_nodes()):
            item_url = node.video_url if node.is_video else node.display_url
            media_items.append(MediaItemDTO(
                index=idx + 1,
                thumbnail_url=get_proxied_thumb(node.display_url),
                is_video=node.is_video,
                formats=_create_format(item_url, node.is_video)
            ))
    else:
        item_url = post.video_url if post.is_video else post.url
        media_items.append(MediaItemDTO(
            index=1,
            thumbnail_url=get_proxied_thumb(post.url),
            is_video=post.is_video,
            formats=_create_format(item_url, post.is_video)
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
