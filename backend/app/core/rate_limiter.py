import hashlib
import time
from fastapi import Request
from app.core.config import settings
from app.core.redis_helper import redis_helper
from app.core.exceptions import AppException
from app.core.logger import logger

def get_license_tier(request: Request) -> str:
    """
    Validate the license key from X-License-Key header using SHA-256 hash.
    """
    key = request.headers.get("X-License-Key")
    if not key:
        return "free"
    
    key_hash = hashlib.sha256(key.strip().encode()).hexdigest()
    if key_hash in settings.ALLOWED_LICENSE_HASHES:
        return "premium"
    
    # If key is provided but invalid, we treat it as free but log a warning
    logger.warning(f"Invalid license key attempt: {key[:4]}...{key[-4:] if len(key) > 8 else ''}")
    return "free"

async def check_rate_limit_and_license(request: Request) -> str:
    """
    FastAPI dependency to validate license key and enforce rate limits using Redis.
    """
    tier = get_license_tier(request)
    ip = request.client.host if request.client else "127.0.0.1"
    endpoint = request.url.path
    
    # Rate limit values based on tier
    limit = settings.PREMIUM_RATE_LIMIT if tier == "premium" else settings.FREE_RATE_LIMIT
    
    # Track rate limit in Redis (bucket by minute)
    current_minute = int(time.time() / 60)
    redis_key = f"rate_limit:{ip}:{endpoint}:{current_minute}"
    
    try:
        count = redis_helper.client.incr(redis_key)
        if count == 1:
            redis_helper.client.expire(redis_key, 60)
    except Exception as e:
        logger.error(f"Redis rate limiter error: {e}. Bypassing rate limit check.")
        request.state.license_tier = tier
        request.state.client_ip = ip
        return tier
        
    if count > limit:
        logger.warning(f"Rate limit exceeded for IP {ip} on {endpoint}. Tier: {tier}. Count: {count}")
        raise AppException(
            code="RATE_LIMIT_EXCEEDED",
            message=f"Bạn đã vượt quá giới hạn yêu cầu ({limit} lượt/phút). Vui lòng thử lại sau.",
            status_code=429,
            is_retryable=True
        )
        
    # Save the computed state to request.state to access in routes
    request.state.license_tier = tier
    request.state.client_ip = ip
    
    # Anonymous tracking: increment total requests and IP stats
    try:
        endpoint_clean = endpoint.split("/")[-1] or "root"
        redis_helper.client.hincrby("stats:total", endpoint_clean, 1)
        redis_helper.client.hincrby(f"stats:ip:{ip}", endpoint_clean, 1)
    except Exception as e:
        logger.error(f"Redis stats tracking error: {e}")
        
    return tier
