from pydantic import BaseModel, Field
from typing import Optional

class JobState(BaseModel):
    job_id: str
    status: str = Field(..., description="Trạng thái: PENDING, PROCESSING, COMPLETED, FAILED")
    progress: float = Field(0.0, description="Phần trăm hoàn thành")
    eta_seconds: Optional[int] = Field(None, description="Thời gian dự kiến còn lại")
    speed_bytes: Optional[float] = Field(None, description="Tốc độ tải (byte/s)")
    download_url: Optional[str] = Field(None, description="Link tải file kết quả nếu COMPLETED")
    error_message: Optional[str] = Field(None, description="Chi tiết lỗi nếu FAILED")
