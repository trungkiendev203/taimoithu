import pytest
import os
import shutil
import time
from unittest.mock import patch
from app.core.config import settings
from app.core.redis_helper import redis_helper
from app.utils.cleanup import cleanup_old_files
from app.worker.tasks import download_video_task

def test_license_key_validation(client):
    """
    Test that sending a valid premium license key unlocks premium tier.
    """
    with patch("app.worker.tasks.download_video_task.delay") as mock_delay:
        headers = {"X-License-Key": "TAIMOITHU_PREMIUM_KEY_2026"}
        response = client.post("/api/v1/download", json={
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "format_id": "best"
        }, headers=headers)
        assert response.status_code == 202
        mock_delay.assert_called_once()
        args = mock_delay.call_args[0]
        # Fourth argument is tier, should be 'premium'
        assert args[3] == "premium"

def test_rate_limiting(client):
    """
    Test that rapid requests are blocked when rate limits are exceeded.
    """
    # Free rate limit is 10 requests/minute. Let's make 11.
    for i in range(11):
        response = client.get("/api/v1/analyze?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        if i < 10:
            assert response.status_code != 429
        else:
            assert response.status_code == 429
            data = response.json()
            assert data["status"] == "error"
            assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"

def test_concurrency_limit(client):
    """
    Test that active concurrent job limits are enforced.
    """
    ip = "testclient"
    
    # Free tier concurrent limit is 1. Add one job first.
    redis_helper.add_active_job(ip, "dummy-job-1")
    
    # Second request should be blocked
    response = client.post("/api/v1/download", json={
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "format_id": "best"
    })
    assert response.status_code == 429
    data = response.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == "CONCURRENT_LIMIT_EXCEEDED"

def test_cleanup_expired_files():
    """
    Test that temporary directories older than the threshold are removed.
    """
    downloads_dir = "downloads"
    test_job_id = "test-expired-job"
    test_dir = os.path.join(downloads_dir, test_job_id)
    os.makedirs(test_dir, exist_ok=True)
    
    test_file = os.path.join(test_dir, "dummy.txt")
    with open(test_file, "w") as f:
        f.write("temp data")
        
    # Backdate the file/directory to 20 minutes ago (1200 seconds)
    twenty_mins_ago = time.time() - 1200
    os.utime(test_file, (twenty_mins_ago, twenty_mins_ago))
    os.utime(test_dir, (twenty_mins_ago, twenty_mins_ago))
    
    # Run cleanup with a threshold of 15 minutes (900 seconds)
    cleanup_old_files(threshold_seconds=900)
    
    assert not os.path.exists(test_dir)

def test_file_size_limit_enforcement():
    """
    Test that files exceeding the size limit trigger task failures.
    """
    job_id = "test-size-limit-job"
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    format_id = "best"
    
    with patch("yt_dlp.YoutubeDL") as mock_ytdl:
        # Configure context manager
        mock_ytdl.return_value.__enter__.return_value = mock_ytdl.return_value
        
        def mock_extract_info(url, download=True):
            # Extract the progress hook passed to yt_dlp
            ydl_args = mock_ytdl.call_args[0][0]
            progress_hook = ydl_args["progress_hooks"][0]
            # Call progress hook with large size (60MB > free limit 50MB)
            progress_hook({
                "status": "downloading",
                "total_bytes": 60 * 1024 * 1024,
                "downloaded_bytes": 1024
            })
            return {}
            
        mock_ytdl.return_value.extract_info = mock_extract_info
        
        # Execute task under free tier
        download_video_task(job_id, url, format_id, tier="free")
        
        state = redis_helper.get_job_state(job_id)
        assert state["status"] == "FAILED"
        assert "vượt quá giới hạn cho phép" in state["error_message"]
