from fastapi import APIRouter
from app.schemas.common import SuccessResponse
from app.core.redis_helper import redis_helper
from datetime import datetime

router = APIRouter()

@router.get("/stats", response_model=SuccessResponse[dict])
def get_usage_stats():
    """
    Lấy số liệu thống kê sử dụng ẩn danh (analyze/download).
    """
    try:
        total_stats = redis_helper.client.hgetall("stats:total")
        total_stats = {k: int(v) for k, v in total_stats.items()}
    except Exception:
        total_stats = {}

    ip_stats = {}
    try:
        # Lấy danh sách các IP từ Redis
        keys = redis_helper.client.keys("stats:ip:*")
        for key in keys[:50]:  # Giới hạn 50 key đầu tiên
            ip = key.replace("stats:ip:", "")
            data = redis_helper.client.hgetall(key)
            ip_stats[ip] = {k: int(v) for k, v in data.items()}
    except Exception:
        pass
        
    # Sắp xếp các IP theo tổng lượng yêu cầu giảm dần
    sorted_ips = sorted(
        ip_stats.items(), 
        key=lambda item: sum(item[1].values()), 
        reverse=True
    )[:10]  # Lấy top 10 IP

    return SuccessResponse(
        data={
            "total": total_stats,
            "top_ips": dict(sorted_ips)
        },
        metadata={"timestamp": datetime.utcnow().isoformat() + "Z"}
    )
