from pydantic import BaseModel, Field
from typing import Any, Generic, TypeVar, Optional, List

DataT = TypeVar("DataT")

class ErrorDetail(BaseModel):
    field: Optional[str] = Field(None, description="Tên trường bị lỗi")
    message: str = Field(..., description="Chi tiết lỗi")

class ErrorData(BaseModel):
    code: str = Field(..., description="Mã lỗi hệ thống", example="INVALID_URL")
    message: str = Field(..., description="Thông báo lỗi hiển thị cho user")
    is_retryable: bool = Field(False, description="Cờ xác định lỗi có thể retry")
    details: Optional[List[ErrorDetail]] = Field(None, description="Danh sách lỗi chi tiết nếu có")

class ResponseMetadata(BaseModel):
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    request_id: Optional[str] = Field(None, description="Client request trace ID")

class SuccessResponse(BaseModel, Generic[DataT]):
    status: str = Field("success", description="Trạng thái response")
    data: DataT = Field(..., description="Payload chính")
    metadata: Optional[ResponseMetadata] = None

class ErrorResponse(BaseModel):
    status: str = Field("error", description="Trạng thái response")
    error: ErrorData
    metadata: Optional[ResponseMetadata] = None
