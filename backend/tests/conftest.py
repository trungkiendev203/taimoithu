import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.redis_helper import redis_helper

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def clean_redis():
    """
    Fixture to clear Redis rate limits and active jobs before every test.
    """
    try:
        keys_to_delete = []
        keys_to_delete.extend(redis_helper.client.keys("rate_limit:*"))
        keys_to_delete.extend(redis_helper.client.keys("active_jobs:*"))
        keys_to_delete.extend(redis_helper.client.keys("job_ip:*"))
        keys_to_delete.extend(redis_helper.client.keys("stats:*"))
        for key in keys_to_delete:
            redis_helper.client.delete(key)
    except Exception:
        pass

