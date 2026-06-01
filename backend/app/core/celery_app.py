from celery import Celery
from app.core.config import settings

# Khởi tạo Celery App
celery_app = Celery(
    "taimoithu_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"]
)

# Cấu hình tuỳ chọn
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_concurrency=2, # Giới hạn 2 luồng tải đồng thời để tránh khóa IP
    task_reject_on_worker_lost=True,
)
