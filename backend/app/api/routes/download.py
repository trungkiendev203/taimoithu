import uuid
import os
import shutil
import asyncio
from fastapi import APIRouter, Request, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse
from app.schemas.common import SuccessResponse, ErrorResponse
from app.schemas.download import DownloadRequest, DownloadResponseData
from app.schemas.job import JobState
from app.core.redis_helper import redis_helper
from app.core.exceptions import AppException
from app.core.config import settings
from app.core.rate_limiter import check_rate_limit_and_license
from app.core.logger import logger
from datetime import datetime

# Trì hoãn import task để tránh circular import nếu có
# from app.worker.tasks import download_video_task

router = APIRouter()

@router.post("", response_model=SuccessResponse[DownloadResponseData], status_code=202)
async def create_download_job(
    req_data: DownloadRequest, 
    request: Request,
    tier: str = Depends(check_rate_limit_and_license)
):
    """
    Tạo một Job tải file mới.
    """
    from app.worker.tasks import download_video_task
    
    req_id = request.headers.get("X-Request-ID")
    meta = {"timestamp": datetime.utcnow().isoformat() + "Z", "request_id": req_id}
    
    ip = request.state.client_ip
    
    # Check concurrent limits
    limit = settings.PREMIUM_MAX_CONCURRENT_JOBS if tier == "premium" else settings.FREE_MAX_CONCURRENT_JOBS
    current_active = redis_helper.get_active_jobs_count(ip)
    if current_active >= limit:
        raise AppException(
            code="CONCURRENT_LIMIT_EXCEEDED",
            message=f"Bạn đã đạt giới hạn {limit} tiến trình tải đồng thời. Vui lòng chờ tiến trình trước hoàn thành.",
            status_code=429
        )
    
    # Sinh Job ID
    job_id = str(uuid.uuid4())
    
    # Track active job
    redis_helper.add_active_job(ip, job_id)
    
    # Lưu trạng thái ban đầu vào Redis
    initial_state = JobState(job_id=job_id, status="PENDING", progress=0.0).model_dump()
    redis_helper.set_job_state(job_id, initial_state)
    
    # Đẩy vào Celery queue
    download_video_task.delay(job_id, req_data.url, req_data.format_id, tier, req_data.item_index)
    
    return SuccessResponse(data=DownloadResponseData(job_id=job_id), metadata=meta)

@router.get("/{job_id}/events")
async def stream_job_events(job_id: str, request: Request):
    """
    Subscribe Server-Sent Events (SSE) để theo dõi tiến trình của 1 Job.
    """
    async def event_generator():
        # Lấy pubsub object từ redis
        pubsub = redis_helper.client.pubsub()
        channel = f"job_events:{job_id}"
        pubsub.subscribe(channel)
        
        import json
        try:
            # Gửi initial state
            state = redis_helper.get_job_state(job_id)
            if state:
                yield {"event": "progress", "data": json.dumps(state)}
                
            # Lắng nghe sự kiện mới
            while True:
                if await request.is_disconnected():
                    break
                    
                message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    yield {"event": "progress", "data": message["data"]}
                await asyncio.sleep(0.5)
        finally:
            pubsub.unsubscribe(channel)
            pubsub.close()
            
    return EventSourceResponse(event_generator())

@router.get("/{job_id}", response_model=SuccessResponse[JobState])
async def get_job_status(job_id: str, request: Request):
    """
    Lấy trạng thái cuối cùng của Job (Fallback API).
    """
    req_id = request.headers.get("X-Request-ID")
    meta = {"timestamp": datetime.utcnow().isoformat() + "Z", "request_id": req_id}
    
    state_dict = redis_helper.get_job_state(job_id)
    if not state_dict:
        raise AppException(code="JOB_NOT_FOUND", message="Không tìm thấy tiến trình tải này", status_code=404)
        
    return SuccessResponse(data=JobState(**state_dict), metadata=meta)

@router.get("/{job_id}/file")
async def download_file(job_id: str, background_tasks: BackgroundTasks):
    """
    Tải file về máy trực tiếp (force download, không phát video trong trình duyệt).
    """
    state_dict = redis_helper.get_job_state(job_id)
    if not state_dict:
        raise AppException(code="JOB_NOT_FOUND", message="Không tìm thấy tiến trình tải này", status_code=404)
    
    if state_dict.get("status") != "COMPLETED":
        raise AppException(code="JOB_NOT_READY", message="File chưa sẵn sàng", status_code=400)
    
    download_url = state_dict.get("download_url", "")
    # download_url format: /static/downloads/{job_id}/{filename}
    # Convert to actual file path
    relative_path = download_url.replace("/static/downloads/", "downloads/")
    file_path = os.path.abspath(relative_path)
    
    if not os.path.exists(file_path):
        raise AppException(code="FILE_NOT_FOUND", message="File đã bị xóa hoặc không tồn tại", status_code=404)
    
    filename = os.path.basename(file_path)
    
    # Background task to clean up temp download folder after download starts/streams
    def cleanup_temp_files():
        job_dir = os.path.join("downloads", job_id)
        if os.path.exists(job_dir):
            logger.info(f"Auto-deleting downloaded files for job {job_id}")
            shutil.rmtree(job_dir, ignore_errors=True)
            
    background_tasks.add_task(cleanup_temp_files)
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",  # Ép trình duyệt tải về thay vì phát
    )

