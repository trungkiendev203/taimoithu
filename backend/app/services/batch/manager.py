import os
import time
import json
import uuid
import zipfile
from datetime import datetime
from typing import List
from app.core.redis_helper import redis_helper
from app.core.logger import logger
from app.services.ytdlp_service import get_base_ydl_opts, execute_with_fallback
from app.services.platform_detector import detect_platform

def initialize_batch(urls: List[str]) -> str:
    batch_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    
    # Init Metadata Hash
    meta = {
        "status": "pending",
        "created_at": now,
        "total_items": str(len(urls)),
        "zip_url": ""
    }
    redis_helper.client.hset(f"batch_job:{batch_id}", mapping=meta)
    redis_helper.client.expire(f"batch_job:{batch_id}", 7200) # 2 hours failsafe TTL
    
    # Init Items Hash
    for idx, url in enumerate(urls):
        item_data = {
            "index": idx,
            "url": url,
            "status": "pending",
            "file_path": "",
            "error_message": ""
        }
        redis_helper.client.hset(f"batch_job:{batch_id}:items", str(idx), json.dumps(item_data))
        
    redis_helper.client.expire(f"batch_job:{batch_id}:items", 7200)
    
    return batch_id

def process_batch(batch_id: str, urls: List[str]):
    try:
        redis_helper.client.hset(f"batch_job:{batch_id}", "status", "processing")
        
        batch_dir = os.path.abspath(f"downloads/batch_{batch_id}")
        items_dir = os.path.join(batch_dir, "items")
        os.makedirs(items_dir, exist_ok=True)
        
        for idx, url in enumerate(urls):
            # Lấy data hiện tại
            item_raw = redis_helper.client.hget(f"batch_job:{batch_id}:items", str(idx))
            if not item_raw:
                continue
            item_data = json.loads(item_raw)
            item_data["status"] = "processing"
            redis_helper.client.hset(f"batch_job:{batch_id}:items", str(idx), json.dumps(item_data))
            
            try:
                try:
                    platform = detect_platform(url)
                except Exception:
                    platform = "unknown"
                    
                base_opts = get_base_ydl_opts(platform)
                outtmpl = os.path.join(items_dir, f"%(title)s_{idx}.%(ext)s")
                base_opts['outtmpl'] = outtmpl
                # Không bắt buột định dạng ở V1, cứ để bestvideo+bestaudio
                
                info, final_file = execute_with_fallback(url, platform, base_opts, download=True)
                
                if info and info.get('title'):
                    item_data["title"] = info.get('title')
                else:
                    item_data["title"] = url # fallback
                
                if final_file and os.path.exists(final_file):
                    item_data["status"] = "completed"
                    item_data["file_path"] = final_file
                else:
                    item_data["status"] = "failed"
                    item_data["error_message"] = "File tải về không tồn tại"
            except Exception as e:
                item_data["status"] = "failed"
                item_data["error_message"] = str(e)
                logger.error(f"Batch item {batch_id}:{idx} failed: {e}")
                
            # Lưu lại trạng thái của item này
            redis_helper.client.hset(f"batch_job:{batch_id}:items", str(idx), json.dumps(item_data))
            
        # Nén ZIP sau khi chạy xong toàn bộ items
        zip_path = os.path.abspath(f"downloads/batch_{batch_id}.zip")
        
        has_files = False
        all_items_raw = redis_helper.client.hgetall(f"batch_job:{batch_id}:items")
        
        # Check xem có file nào thành công không
        for key, value in all_items_raw.items():
            item = json.loads(value)
            if item["status"] == "completed" and item["file_path"] and os.path.exists(item["file_path"]):
                has_files = True
                break
                
        if has_files:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for key, value in all_items_raw.items():
                    item = json.loads(value)
                    if item["status"] == "completed" and item["file_path"] and os.path.exists(item["file_path"]):
                        filename = os.path.basename(item["file_path"])
                        zipf.write(item["file_path"], arcname=filename)
                        
            redis_helper.client.hset(f"batch_job:{batch_id}", "zip_url", f"/api/v1/batch/download/batch_{batch_id}.zip")
            redis_helper.client.hset(f"batch_job:{batch_id}", "status", "completed")
        else:
            redis_helper.client.hset(f"batch_job:{batch_id}", "status", "failed")
            
    except Exception as e:
        logger.error(f"Batch process {batch_id} failed catastrophically: {e}")
        redis_helper.client.hset(f"batch_job:{batch_id}", "status", "failed")

def get_batch_status(batch_id: str) -> dict:
    meta_raw = redis_helper.client.hgetall(f"batch_job:{batch_id}")
    if not meta_raw:
        return None
        
    meta = {k.decode('utf-8') if isinstance(k, bytes) else k: v.decode('utf-8') if isinstance(v, bytes) else v for k, v in meta_raw.items()}
    
    items_raw = redis_helper.client.hgetall(f"batch_job:{batch_id}:items")
    items = []
    completed_count = 0
    for key, val in items_raw.items():
        item = json.loads(val.decode('utf-8') if isinstance(val, bytes) else val)
        items.append(item)
        if item["status"] == "completed":
            completed_count += 1
            
    items.sort(key=lambda x: x["index"])
    
    return {
        "batch_id": batch_id,
        "status": meta.get("status", "unknown"),
        "created_at": meta.get("created_at", ""),
        "total_items": int(meta.get("total_items", 0)),
        "completed_items": completed_count,
        "zip_url": meta.get("zip_url", ""),
        "items": items
    }
