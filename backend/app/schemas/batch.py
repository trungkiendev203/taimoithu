from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class BatchCreateRequest(BaseModel):
    urls: List[str]

class BatchItemStatus(BaseModel):
    index: int
    url: str
    title: Optional[str] = None
    status: str
    file_path: Optional[str] = None
    error_message: Optional[str] = None

class BatchStatusResponse(BaseModel):
    batch_id: str
    status: str
    created_at: str
    total_items: int
    completed_items: int
    zip_url: Optional[str] = None
    items: List[BatchItemStatus]
