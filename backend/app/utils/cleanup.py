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
        for entry in os.listdir(downloads_dir):
            entry_path = os.path.join(downloads_dir, entry)
            # Only clean up subfolders representing specific jobs (e.g. uuid-like folders)
            if os.path.isdir(entry_path) and entry != "test_scratch_job" and entry != "test_scratch_job2" and entry != "test_scratch_job3":
                # Check directory modification time
                mtime = os.path.getmtime(entry_path)
                age = now - mtime
                if age > threshold_seconds:
                    logger.info(f"Removing expired temp folder: {entry_path} (Age: {int(age)}s)")
                    shutil.rmtree(entry_path, ignore_errors=True)
                    deleted_count += 1
        logger.info(f"Cleanup completed. Removed {deleted_count} expired folder(s).")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
