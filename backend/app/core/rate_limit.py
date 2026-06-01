# Stub for Rate Limiting
# Phase 1: In-memory or simple pass-through. Later, this will connect to Redis.

from fastapi import Request

async def check_rate_limit(request: Request):
    """
    Check if the IP or Client-ID has exceeded the quota.
    Phase 1: Always passes.
    """
    return True
