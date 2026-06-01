from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.schemas.common import ErrorResponse, ErrorData, ErrorDetail
from app.core.logger import logger
from datetime import datetime

class AppException(Exception):
    def __init__(self, code: str, message: str, is_retryable: bool = False, status_code: int = 400):
        self.code = code
        self.message = message
        self.is_retryable = is_retryable
        self.status_code = status_code

async def app_exception_handler(request: Request, exc: AppException):
    req_id = request.headers.get("X-Request-ID")
    meta = {"timestamp": datetime.utcnow().isoformat() + "Z", "request_id": req_id}
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=ErrorData(
                code=exc.code,
                message=exc.message,
                is_retryable=exc.is_retryable
            ),
            metadata=meta
        ).model_dump()
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    req_id = request.headers.get("X-Request-ID")
    meta = {"timestamp": datetime.utcnow().isoformat() + "Z", "request_id": req_id}
    details = [ErrorDetail(field=str(err["loc"][-1]), message=err["msg"]) for err in exc.errors()]
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error=ErrorData(
                code="VALIDATION_ERROR",
                message="Dữ liệu đầu vào không hợp lệ",
                is_retryable=False,
                details=details
            ),
            metadata=meta
        ).model_dump()
    )

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    req_id = request.headers.get("X-Request-ID")
    meta = {"timestamp": datetime.utcnow().isoformat() + "Z", "request_id": req_id}
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=ErrorData(
                code="INTERNAL_SERVER_ERROR",
                message="Đã có lỗi xảy ra từ phía máy chủ.",
                is_retryable=True
            ),
            metadata=meta
        ).model_dump()
    )
