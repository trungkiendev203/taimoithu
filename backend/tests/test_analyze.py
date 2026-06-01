def test_analyze_invalid_url(client):
    response = client.get("/api/v1/analyze?url=http://localhost")
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == "INVALID_URL"

def test_analyze_unsupported_platform(client):
    response = client.get("/api/v1/analyze?url=https://example.com/video")
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == "UNSUPPORTED_PLATFORM"

# Note: We skip testing valid yt-dlp extraction in basic unit tests to avoid 
# downloading data from internet during CI, or we should mock yt-dlp service.
