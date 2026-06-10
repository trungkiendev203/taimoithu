import os
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse
from app.schemas.common import SuccessResponse
from app.schemas.batch import BatchCreateRequest, BatchStatusResponse
from app.services.batch.manager import initialize_batch, process_batch, get_batch_status
from app.core.exceptions import AppException

router = APIRouter()

@router.post("/create", response_model=SuccessResponse[dict], status_code=202)
async def create_batch(req: BatchCreateRequest, background_tasks: BackgroundTasks):
    if not req.urls:
        raise AppException("INVALID_REQUEST", "Danh sách URL trống", 400)
    if len(req.urls) > 5:
        raise AppException("LIMIT_EXCEEDED", "Tối đa 5 link mỗi batch", 400)
        
    batch_id = initialize_batch(req.urls)
    
    # Fire and forget (V1 limitation: won't survive restart)
    background_tasks.add_task(process_batch, batch_id, req.urls)
    
    return SuccessResponse(data={"batch_id": batch_id})

@router.get("/{batch_id}", response_model=SuccessResponse[BatchStatusResponse])
async def get_status(batch_id: str):
    data = get_batch_status(batch_id)
    if not data:
        raise AppException("NOT_FOUND", "Batch không tồn tại hoặc đã hết hạn", 404)
        
    return SuccessResponse(data=data)

@router.get("/download/batch_{batch_id}.zip")
@router.get("/{batch_id}/download") # Keep old route for backwards compatibility
async def download_zip(batch_id: str):
    zip_path = os.path.abspath(f"downloads/batch_{batch_id}.zip")
    if not os.path.exists(zip_path):
        raise AppException("NOT_FOUND", "File ZIP không tồn tại hoặc đã bị xoá", 404)
        
    return FileResponse(
        path=zip_path,
        filename=f"batch_{batch_id}.zip",
        media_type="application/zip"
    )
