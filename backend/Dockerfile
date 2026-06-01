FROM python:3.11-slim

WORKDIR /app

# Install system dependencies:
# - ffmpeg: for merging video+audio streams
# - curl: for health checks
# - nodejs: REQUIRED by yt-dlp to decrypt YouTube signatures (without it, only 360p is returned)
RUN apt-get update && apt-get install -y ffmpeg curl nodejs && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
