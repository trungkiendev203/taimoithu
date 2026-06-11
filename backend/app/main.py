from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.routes import health, analyze, download, monitor, batch, feedback
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
    expose_headers=["Content-Disposition"],
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
app.include_router(batch.router, prefix=f"{settings.API_V1_STR}/batch", tags=["batch"])
app.include_router(feedback.router, prefix=f"{settings.API_V1_STR}/feedback", tags=["feedback"])

@app.on_event("startup")
async def startup_event():
    import asyncio
    from app.utils.cleanup import cleanup_old_files
    from app.core.logger import logger
    from app.services.telegram_bot import start_telegram_bot_thread, check_cookie_periodic
    
    # Khởi động Telegram Bot
    start_telegram_bot_thread()
    
    async def background_tasks_loop():
        # Lần đầu chờ 10s
        await asyncio.sleep(10)
        
        # Biến đếm để chạy check_cookie_periodic mỗi 1 tiếng (3600s / 600s = 6 lần cleanup loop)
        loop_count = 0
        
        while True:
            try:
                cleanup_old_files(900)  # Xóa folder cũ hơn 15 phút
            except Exception as e:
                logger.error(f"Error in background cleanup loop: {e}")
                
            try:
                # Mỗi 1 tiếng chạy check cookie một lần
                if loop_count % 6 == 0:
                    await asyncio.to_thread(check_cookie_periodic)
            except Exception as e:
                logger.error(f"Error checking cookie periodic: {e}")
                
            loop_count += 1
            await asyncio.sleep(600)  # Chạy lại sau 10 phút
            
    asyncio.create_task(background_tasks_loop())
    logger.info("Background tasks loop initialized.")

@app.get("/", tags=["root"])
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}
