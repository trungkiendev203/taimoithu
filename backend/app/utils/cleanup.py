import os
import shutil
import time
from app.core.logger import logger

def cleanup_old_files(threshold_seconds: int = 900):
    """
    Scans the 'downloads' directory and removes subdirectories older than the threshold.
    """
    downloads_dir = os.path.abspath("downloads")
    if not os.path.exists(downloads_dir):
        return
        
    logger.info("Running automatic temp files cleanup...")
    now = time.time()
    deleted_count = 0
    
    try:
        from app.core.redis_helper import redis_helper
        
        for entry in os.listdir(downloads_dir):
            entry_path = os.path.join(downloads_dir, entry)
            
            # Xử lý thư mục (Jobs lẻ hoặc batch_uuid)
            if os.path.isdir(entry_path) and entry not in ["test_scratch_job", "test_scratch_job2", "test_scratch_job3"]:
                mtime = os.path.getmtime(entry_path)
                age = now - mtime
                
                # Default threshold cho job thường, 3600 cho batch
                eff_threshold = 3600 if entry.startswith("batch_") else threshold_seconds
                
                if age > eff_threshold:
                    logger.info(f"Removing expired folder: {entry_path} (Age: {int(age)}s)")
                    shutil.rmtree(entry_path, ignore_errors=True)
                    deleted_count += 1
                    
                    # Nếu là batch, xóa luôn redis keys
                    if entry.startswith("batch_"):
                        batch_id = entry.replace("batch_", "")
                        try:
                            redis_helper.client.delete(f"batch_job:{batch_id}")
                            redis_helper.client.delete(f"batch_job:{batch_id}:items")
                        except Exception as e:
                            pass
                            
            # Xử lý file (ZIP của batch)
            elif os.path.isfile(entry_path) and entry.startswith("batch_") and entry.endswith(".zip"):
                mtime = os.path.getmtime(entry_path)
                age = now - mtime
                if age > 3600:
                    logger.info(f"Removing expired ZIP: {entry_path} (Age: {int(age)}s)")
                    os.remove(entry_path)
                    deleted_count += 1
                    
        logger.info(f"Cleanup completed. Removed {deleted_count} expired item(s).")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
