from fastapi import APIRouter
import shutil
import os
from app.schemas.common import SuccessResponse
from app.core.config import settings
from app.core.redis_helper import redis_helper
from app.core.celery_app import celery_app
from datetime import datetime

router = APIRouter()

@router.get("/health", response_model=SuccessResponse[dict])
def health_check():
    """
    Health check nâng cao cho API, Redis, Celery worker và Dung lượng ổ đĩa.
    """
    # 1. Check Redis
    try:
        redis_helper.client.ping()
        redis_status = "connected"
    except Exception as e:
        redis_status = f"error: {str(e)}"
        
    # 2. Check Celery Worker
    try:
        # Sử dụng timeout ngắn để tránh treo API nếu worker bị sập
        inspect = celery_app.control.inspect(timeout=1.0)
        ping_result = inspect.ping()
        worker_status = "active" if ping_result else "inactive"
    except Exception as e:
        worker_status = f"error: {str(e)}"
        
    # 3. Check Disk Space
    try:
        downloads_dir = "downloads"
        os.makedirs(downloads_dir, exist_ok=True)
        total, used, free = shutil.disk_usage(downloads_dir)
        disk_status = {
            "total_mb": round(total / (1024**2), 2),
            "used_mb": round(used / (1024**2), 2),
            "free_mb": round(free / (1024**2), 2),
            "free_percent": round((free / total) * 100, 2) if total > 0 else 0
        }
    except Exception as e:
        disk_status = f"error: {str(e)}"

    overall_status = "ok"
    if "error" in redis_status or worker_status == "inactive" or "error" in worker_status:
        overall_status = "degraded"

    return SuccessResponse(
        data={
            "status": overall_status,
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "redis": redis_status,
            "worker": worker_status,
            "disk": disk_status
        },
        metadata={"timestamp": datetime.utcnow().isoformat() + "Z"}
    )
