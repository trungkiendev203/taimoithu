from fastapi import APIRouter, Query, Request, Depends, Response
import httpx
import base64
from app.schemas.common import SuccessResponse, ErrorResponse
from app.schemas.analyze import AnalyzeResponseData
from app.services.platform_detector import detect_platform
from app.utils.url_validator import is_safe_url
from app.services.ytdlp_service import extract_metadata
from app.services.helpers import detect_referer_for_cdn
from app.core.exceptions import AppException
from app.core.rate_limiter import check_rate_limit_and_license
from datetime import datetime

router = APIRouter()

@router.get("/analyze", response_model=SuccessResponse[AnalyzeResponseData], responses={400: {"model": ErrorResponse}})
async def analyze_url(
    url: str = Query(..., description="URL to analyze", example="https://www.youtube.com/watch?v=dQw4w9WgXcQ"), 
    request: Request = None,
    tier: str = Depends(check_rate_limit_and_license)
):
    """
    Analyze a URL to get video metadata and available formats.
    """
    req_id = request.headers.get("X-Request-ID") if request else None
    meta = {"timestamp": datetime.utcnow().isoformat() + "Z", "request_id": req_id}
    
    # 1. URL Security Validation
    if not is_safe_url(url):
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=400, 
            content={"success": False, "message": "Invalid video URL"}
        )
    
    # 2. Platform Detection
    try:
        platform = detect_platform(url)
    except ValueError:
        raise AppException(
            code="UNSUPPORTED_PLATFORM",
            message="Nền tảng chưa được hỗ trợ.",
            is_retryable=False,
            status_code=400
        )
        
    # 3. Extract Metadata via yt-dlp
    try:
        data = await extract_metadata(url)
        return SuccessResponse(data=data, metadata=meta)
    except AppException as ae:
        raise ae
    except Exception as e:
        raise AppException(
            code="EXTRACTION_ERROR",
            message=str(e),
            is_retryable=True,
            status_code=400
        )

@router.get("/proxy-image")
async def proxy_image(url: str):
    """
    Proxy an image URL to bypass CORS and Cross-Origin-Resource-Policy.
    Used for Instagram CDN URLs.
    """
    try:
        if url.startswith("base64:"):
            encoded = url[7:]
            # Tương thích ngược: đổi khoảng trắng thành +
            encoded = encoded.replace(" ", "+")
            # Thêm padding nếu thiếu
            encoded += "=" * ((-len(encoded)) % 4)
            url = base64.urlsafe_b64decode(encoded).decode("utf-8")
            
        # Detect đúng Referer dựa trên CDN domain (Douyin, TikTok, Instagram...)
        referer = detect_referer_for_cdn(url) or "https://www.google.com/"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", 
                "Referer": referer
            })
            return Response(content=resp.content, media_type=resp.headers.get("content-type", "image/jpeg"))
    except Exception as e:
        print(f"Proxy Image Error: {str(e)} - Source URL: {url}")
        return Response(content=f"Proxy error: {str(e)}", status_code=400)
