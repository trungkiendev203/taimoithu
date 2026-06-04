"""Douyin video metadata extraction using Playwright."""
import asyncio
import json
import re
import base64
import urllib.parse
from playwright.async_api import async_playwright
from app.schemas.analyze import AnalyzeResponseData, FormatDTO, MediaItemDTO
from app.services.helpers import get_proxied_thumb, load_playwright_cookies

MAX_RETRIES = 2


def normalize_douyin_url(url: str) -> str:
    """Normalize Douyin URL variants to /video/{id} format."""
    modal_match = re.search(r'modal_id=(\d+)', url)
    if modal_match:
        normalized = f"https://www.douyin.com/video/{modal_match.group(1)}"
        print(f"Douyin: Normalized URL: {url} -> {normalized}")
        return normalized

    note_match = re.search(r'/note/(\d+)', url)
    if note_match:
        normalized = f"https://www.douyin.com/video/{note_match.group(1)}"
        print(f"Douyin: Normalized URL: {url} -> {normalized}")
        return normalized

    # Short links (v.douyin.com, iesdouyin.com) — Playwright will follow redirect
    return url


async def _run_playwright(url: str) -> dict:
    """Core Playwright extraction. Returns raw extracted data dict."""
    video_urls = []
    title = "Douyin Video"
    author_name = "Unknown"
    duration = 0
    main_thumbnail = None

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
            ]
        )

        pw_cookies = load_playwright_cookies()

        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/130.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800}
        )
        if pw_cookies:
            print(f"Loaded {len(pw_cookies)} cookies into Playwright.")
            await context.add_cookies(pw_cookies)
        else:
            print("NO cookies loaded into Playwright.")

        page = await context.new_page()
        await page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        async def handle_response(response):
            if "aweme/v1/web/aweme/detail" not in response.url:
                return
            print("Playwright: Intercepted aweme detail API")
            try:
                text = await response.text()
                data = json.loads(text)
                aweme = data.get("aweme_detail", {})

                nonlocal title, author_name, duration, main_thumbnail
                title = aweme.get("desc", title)
                author_name = aweme.get("author", {}).get("nickname", author_name)
                duration = aweme.get("video", {}).get("duration", 0) // 1000

                video = aweme.get("video", {})
                cover = video.get("cover", {}).get("url_list", [None])[0]
                if cover:
                    main_thumbnail = cover

                play_addr = video.get("play_addr", {})
                url_list = play_addr.get("url_list", [])
                if url_list:
                    print(f"Playwright: Found {len(url_list)} URLs")
                    video_urls.extend(url_list)
            except Exception as e:
                print(f"Playwright: Error parsing response: {e}")

        page.on("response", handle_response)

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(5)

            # Fallback 1: extract from <video> DOM element
            if not video_urls:
                video_src = await page.evaluate('''() => {
                    const video = document.querySelector('video');
                    if (video) {
                        const source = video.querySelector('source');
                        if (source && source.src) return source.src;
                        return video.src;
                    }
                    return null;
                }''')
                if video_src and video_src.startswith("http"):
                    print(f"Playwright: Extracted from DOM: {video_src}")
                    video_urls.append(video_src)

            # Fallback 2: parse RENDER_DATA script tag
            if not video_urls:
                render_el = page.locator("#RENDER_DATA").first
                if await render_el.count() > 0:
                    raw = await render_el.inner_text()
                    content = urllib.parse.unquote(raw)
                    data = json.loads(content)
                    for _key, val in data.items():
                        if not isinstance(val, dict) or "aweme" not in val:
                            continue
                        aweme = val.get("aweme", {}).get("detail", {})
                        title = aweme.get("desc", title)
                        author_name = aweme.get("author", {}).get("nickname", author_name)
                        video = aweme.get("video", {})
                        duration = video.get("duration", 0) // 1000
                        cover = video.get("cover", {}).get("url_list", [None])[0]
                        if cover:
                            main_thumbnail = cover
                        play_list = video.get("play_addr", {}).get("url_list", [])
                        video_urls.extend(play_list)
        except Exception as e:
            raise Exception(f"Lỗi truy cập Douyin Playwright: {str(e)}")
        finally:
            await browser.close()

    return {
        "video_urls": video_urls,
        "title": title,
        "author_name": author_name,
        "duration": duration,
        "main_thumbnail": main_thumbnail,
    }


async def extract_douyin_playwright(url: str) -> AnalyzeResponseData:
    """Extract Douyin video metadata using Playwright with retry support."""
    url = normalize_douyin_url(url)

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            result = await _run_playwright(url)
            if result["video_urls"]:
                break
            last_error = Exception("Không tìm thấy video URL từ Douyin.")
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                print(f"Playwright attempt {attempt + 1} failed: {e}. Retrying...")
                await asyncio.sleep(2)
    else:
        raise last_error or Exception("Không thể lấy video URL từ Douyin bằng Playwright.")

    # Deduplicate and pick best URL
    video_urls = list(dict.fromkeys(result["video_urls"]))
    best_url = video_urls[0]
    b64 = base64.urlsafe_b64encode(best_url.encode('utf-8')).decode('utf-8').rstrip('=')

    media_items = [
        MediaItemDTO(
            index=1,
            thumbnail_url=get_proxied_thumb(result["main_thumbnail"]),
            is_video=True,
            formats=[FormatDTO(
                format_id=f"direct_url:{b64}",
                quality_label="Video (Không Logo)",
                type="video", has_audio=True, has_video=True,
                video_codec="auto", audio_codec="auto",
                estimated_size_bytes=None
            )]
        )
    ]

    return AnalyzeResponseData(
        title=result["title"],
        author_name=result["author_name"],
        author_avatar=None,
        thumbnail_url=get_proxied_thumb(result["main_thumbnail"]),
        duration_seconds=result["duration"],
        formats=[],
        media_items=media_items
    )
