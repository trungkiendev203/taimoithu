import pytest
from unittest.mock import patch

def test_create_download_job(client):
    with patch("app.worker.tasks.download_video_task.delay") as mock_delay:
        response = client.post("/api/v1/download", json={
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "format_id": "best"
        })
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "success"
        assert "job_id" in data["data"]
        
        mock_delay.assert_called_once()
        # Verify call args
        args = mock_delay.call_args[0]
        assert args[1] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert args[2] == "best"

def test_get_job_status_not_found(client):
    response = client.get("/api/v1/download/not-exist-job")
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == "JOB_NOT_FOUND"
