import redis
import json
from app.core.config import settings

class RedisHelper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisHelper, cls).__new__(cls)
            cls._instance.client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        return cls._instance

    def publish_job_event(self, job_id: str, event_data: dict):
        """Publish event to SSE channel"""
        channel = f"job_events:{job_id}"
        self.client.publish(channel, json.dumps(event_data))

    def set_job_state(self, job_id: str, state_data: dict):
        """Lưu trạng thái mới nhất vào cache"""
        self.client.set(f"job_state:{job_id}", json.dumps(state_data), ex=86400) # Hết hạn sau 1 ngày

    def get_job_state(self, job_id: str) -> dict:
        data = self.client.get(f"job_state:{job_id}")
        if data:
            return json.loads(data)
        return None

    def add_active_job(self, ip: str, job_id: str):
        """Thêm job vào danh sách đang chạy của IP này"""
        self.client.sadd(f"active_jobs:{ip}", job_id)
        self.client.expire(f"active_jobs:{ip}", 3600)  # Giới hạn TTL 1 tiếng chống leak
        self.client.set(f"job_ip:{job_id}", ip, ex=7200)

    def remove_active_job(self, job_id: str):
        """Xóa job khỏi danh sách đang chạy của IP tương ứng"""
        ip = self.client.get(f"job_ip:{job_id}")
        if ip:
            self.client.srem(f"active_jobs:{ip}", job_id)
            self.client.delete(f"job_ip:{job_id}")

    def get_active_jobs_count(self, ip: str) -> int:
        """Lấy số lượng job đang chạy của IP này"""
        return self.client.scard(f"active_jobs:{ip}")

redis_helper = RedisHelper()
