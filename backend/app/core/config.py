from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import hashlib

class Settings(BaseSettings):
    PROJECT_NAME: str = "Tải Mọi Thứ - Backend"
    VERSION: str = "0.5.0"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"]

    # yt-dlp config
    YTDLP_TIMEOUT: int = 15
    YTDLP_COOKIES_FILE: str = ""
    
    # Docker/DB Placeholders for Phase 2/3
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/taimoithu"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Evil0ctal Douyin/TikTok API (Docker service default, override for local dev)
    EVIL0CTAL_URL: str = "http://evil0ctal:80"

    # Phase 5 Resource Limits
    FREE_MAX_FILE_SIZE_MB: int = 10000
    PREMIUM_MAX_FILE_SIZE_MB: int = 20000  # 20 GB
    FREE_RATE_LIMIT: int = 100            # requests/minute (Increased for testing)
    PREMIUM_RATE_LIMIT: int = 300         # requests/minute
    FREE_MAX_CONCURRENT_JOBS: int = 10
    PREMIUM_MAX_CONCURRENT_JOBS: int = 30
    
    # Key settings
    SAMPLE_LICENSE_KEY: str = "TAIMOITHU_PREMIUM_KEY_2026"
    ALLOWED_LICENSE_HASHES: List[str] = []

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)

settings = Settings()

# Dynamically ensure sample license key hash is loaded
sample_hash = hashlib.sha256(settings.SAMPLE_LICENSE_KEY.encode()).hexdigest()
if sample_hash not in settings.ALLOWED_LICENSE_HASHES:
    settings.ALLOWED_LICENSE_HASHES.append(sample_hash)

