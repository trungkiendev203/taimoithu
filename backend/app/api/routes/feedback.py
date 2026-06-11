from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, Field
import httpx
import logging
from app.core.config import settings
from app.schemas.common import SuccessResponse, ErrorResponse

router = APIRouter()
logger = logging.getLogger(__name__)

class FeedbackRequest(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    email: str | None = Field(default=None, max_length=150)
    message: str = Field(..., min_length=5, max_length=1000)

async def send_telegram_message(text: str):
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
    if not chat_id:
        chat_id = getattr(settings, 'TELEGRAM_ADMIN_ID', None)
    
    if not token or not chat_id:
        logger.warning("Telegram token or chat_id is missing. Feedback not sent to Telegram.")
        return
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to send feedback to Telegram: {e}")

@router.post("", response_model=SuccessResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def submit_feedback(data: FeedbackRequest, background_tasks: BackgroundTasks):
    """
    Nhận feedback từ user và gửi về Telegram Bot.
    """
    from datetime import datetime
    
    # Chuẩn bị nội dung
    name_str = data.name.strip() if data.name else "Ẩn danh"
    email_str = data.email.strip() if data.email else "Không cung cấp"
    message_str = data.message.strip()
    
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # HTML formatting for Telegram
    text = (
        f"🔔 <b>Feedback Mới</b>\n\n"
        f"👤 <b>Tên:</b> {name_str}\n"
        f"📧 <b>Email:</b> {email_str}\n\n"
        f"💬 <b>Nội dung:</b>\n{message_str}\n\n"
        f"🕒 <b>Thời gian:</b> {time_str}"
    )
    
    # Gửi qua background task để không block request
    background_tasks.add_task(send_telegram_message, text)
    
    return SuccessResponse(data={"status": "received", "message": "Feedback submitted successfully"})
