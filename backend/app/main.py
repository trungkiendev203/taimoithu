from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.routes import health, analyze, download, monitor
from app.core.exceptions import (
    AppException, 
    app_exception_handler, 
    validation_exception_handler, 
    global_exception_handler
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="API for Tải Mọi Thứ - Video Downloader (Phase 2)",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Static Files (Phase 3 fake S3)
import os
os.makedirs("downloads", exist_ok=True)
app.mount("/static/downloads", StaticFiles(directory="downloads"), name="downloads")

# Routers
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])
app.include_router(analyze.router, prefix=settings.API_V1_STR, tags=["analyze"])
app.include_router(download.router, prefix=f"{settings.API_V1_STR}/download", tags=["download"])
app.include_router(monitor.router, prefix=settings.API_V1_STR, tags=["monitor"])

@app.on_event("startup")
async def startup_event():
    import asyncio
    from app.utils.cleanup import cleanup_old_files
    from app.core.logger import logger
    
    async def cleanup_loop():
        # Dọn dẹp thư mục downloads định kỳ mỗi 10 phút
        await asyncio.sleep(10)
        while True:
            try:
                cleanup_old_files(900)  # Xóa folder cũ hơn 15 phút
            except Exception as e:
                logger.error(f"Error in background cleanup loop: {e}")
            await asyncio.sleep(600)  # Chạy lại sau 10 phút
            
    asyncio.create_task(cleanup_loop())
    logger.info("Background cleanup loop initialized.")

@app.get("/", tags=["root"])
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}
