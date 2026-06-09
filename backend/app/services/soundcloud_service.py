import os
import json
import subprocess
import asyncio
from app.schemas.analyze import AnalyzeResponseData, FormatDTO
from app.core.exceptions import AppException
from app.core.logger import logger

def call_soundcloud_cli(action: str, url: str, output_path: str = None) -> dict:
    cli_path = os.path.join(os.path.dirname(__file__), "soundcloud_cli.js")
    
    args = ["node", cli_path, action, url]
    if output_path:
        args.append(output_path)
        
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            err_output = result.stderr.strip()
            try:
                err_json = json.loads(err_output)
                error_msg = err_json.get("error", "Unknown error")
            except:
                error_msg = err_output
            raise AppException("SOUNDCLOUD_ERROR", f"Lỗi lấy thông tin SoundCloud: {error_msg}", status_code=400)
            
        output = result.stdout.strip()
        return json.loads(output)
        
    except subprocess.TimeoutExpired:
        raise AppException("TIMEOUT", "Quá thời gian xử lý SoundCloud", status_code=504)
    except Exception as e:
        if isinstance(e, AppException):
            raise e
        raise AppException("SOUNDCLOUD_CLI_FAILED", f"Không thể gọi NodeJS CLI: {str(e)}", status_code=500)

async def extract_soundcloud(url: str) -> AnalyzeResponseData:
    try:
        info = await asyncio.to_thread(call_soundcloud_cli, "info", url)
        
        duration_ms = info.get("duration")
        duration_sec = int(duration_ms / 1000) if duration_ms else None
        
        formats = [
            FormatDTO(
                format_id="soundcloud_audio",
                quality_label="Chỉ Âm thanh (MP3)",
                type="audio",
                has_audio=True,
                has_video=False,
                video_codec="none",
                audio_codec="mp3",
                estimated_size_bytes=None
            )
        ]
        
        return AnalyzeResponseData(
            title=info.get("title", "SoundCloud Audio"),
            author_name=info.get("uploader", "Unknown"),
            thumbnail_url=info.get("thumbnail"),
            duration_seconds=duration_sec,
            formats=formats,
            media_items=[]
        )
    except Exception as e:
        logger.error(f"SoundCloud extraction failed: {str(e)}")
        raise e

def download_soundcloud(url: str, final_file: str):
    try:
        call_soundcloud_cli("download", url, final_file)
    except Exception as e:
        logger.error(f"SoundCloud download failed: {str(e)}")
        raise e
