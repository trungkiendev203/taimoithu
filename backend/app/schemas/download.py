from pydantic import BaseModel, Field
from typing import List, Optional

class DownloadRequest(BaseModel):
    url: str = Field(..., description="URL của video cần tải", example="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    format_id: str = Field("best", description="ID của định dạng muốn tải, lấy từ API analyze")
    item_index: Optional[int] = Field(None, description="Vị trí mục muốn tải (1-based), dùng cho Instagram/Playlist")

class BatchDownloadRequest(BaseModel):
    items: List[DownloadRequest] = Field(..., description="Danh sách các video cần tải")

class DownloadResponseData(BaseModel):
    job_id: str = Field(..., description="ID của tiến trình tải để theo dõi trạng thái")
