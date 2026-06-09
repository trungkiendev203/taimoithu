import asyncio
from app.services.evil0ctal_service import extract_evil0ctal
from app.services.ytdlp_service import extract_metadata

async def test_bilibili():
    url = "https://www.bilibili.com/video/BV1Tf7k6yEiU/"
    print(f"Testing Bilibili URL: {url}")
    print("-" * 50)
    
    # 1. Test Evil0ctal parser directly
    print("1. Đang test trực tiếp parser Evil0ctal...")
    try:
        evil_data = await extract_evil0ctal(url, "bilibili")
        print(f"[Evil0ctal] Trích xuất thành công: {evil_data.title}")
        print(f"[Evil0ctal] Media Items count: {len(evil_data.media_items)}")
        for i, item in enumerate(evil_data.media_items):
            print(f"  - Item {i+1}: is_video={item.is_video}")
            for f in item.formats:
                print(f"    - Format: {f.quality_label} | ID: {f.format_id[:50]}...")
    except Exception as e:
        print(f"[Evil0ctal] LỖI HOẶC FALLBACK: {str(e)}")
        
    print("-" * 50)
    
    # 2. Test luồng chính (extract_metadata)
    print("2. Đang test luồng chính extract_metadata (kiểm tra Fallback)...")
    try:
        final_data = await extract_metadata(url)
        print(f"[Main Router] Kết quả cuối cùng: {final_data.title}")
        print(f"[Main Router] Thời lượng: {final_data.duration_seconds} giây")
        print(f"[Main Router] Media Items count: {len(final_data.media_items)}")
        
        # In format của yt-dlp/evil0ctal
        if final_data.formats:
            print("[Main Router] Formats gốc (yt-dlp):")
            for f in final_data.formats:
                print(f"  - {f.quality_label}: {f.format_id[:50]}")
        else:
            print("[Main Router] Formats lấy từ media_items (Evil0ctal):")
            for item in final_data.media_items:
                for f in item.formats:
                    print(f"  - {f.quality_label}: {f.format_id[:50]}...")
                    
        print("\n=> TEST HOÀN TẤT THÀNH CÔNG")
    except Exception as e:
        print(f"\n=> TEST THẤT BẠI: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_bilibili())
