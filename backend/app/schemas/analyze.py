from pydantic import BaseModel, Field
from typing import List, Optional

class FormatDTO(BaseModel):
    format_id: str = Field(..., description="ID của format yt-dlp trả về")
    quality_label: str = Field(..., description="Nhãn chất lượng (vd: 1080p, Ảnh)")
    type: str = Field(..., description="video, audio, hoặc image")
    has_audio: bool = Field(..., description="Video có tiếng không")
    has_video: bool = Field(..., description="Có hình không (hoặc là audio only/image)")
    video_codec: Optional[str] = Field(None, description="Mã video codec")
    audio_codec: Optional[str] = Field(None, description="Mã audio codec")
    estimated_size_bytes: Optional[int] = Field(None, description="Dung lượng ước tính")

class MediaItemDTO(BaseModel):
    index: int = Field(..., description="Vị trí của media trong bài đăng (bắt đầu từ 1)")
    thumbnail_url: Optional[str] = Field(None, description="Ảnh xem trước của mục này")
    is_video: bool = Field(..., description="Đánh dấu mục này là video hay ảnh")
    formats: List[FormatDTO] = Field(default_factory=list, description="Định dạng hỗ trợ tải cho riêng mục này")

class AnalyzeResponseData(BaseModel):
    title: str = Field(..., description="Tên video hoặc bài viết")
    author_name: Optional[str] = Field(None, description="Tác giả")
    author_avatar: Optional[str] = Field(None, description="Ảnh đại diện tác giả")
    # Giữ lại các trường cũ cho tính tương thích (YouTube/TikTok 1 video)
    thumbnail_url: Optional[str] = Field(None, description="Ảnh bìa video (dùng khi không có media_items)")
    duration_seconds: Optional[int] = Field(None, description="Thời lượng")
    formats: List[FormatDTO] = Field(default_factory=list, description="Danh sách định dạng hỗ trợ (dùng chung)")
    
    # Trường mới cho Instagram Carousel
    media_items: List[MediaItemDTO] = Field(default_factory=list, description="Danh sách các media trong bài viết (ảnh/video)")
