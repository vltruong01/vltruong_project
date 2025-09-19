FROM python:3.11-slim

# 1) System deps (nhẹ)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Cài deps Python
#    - Dùng extra index của PyTorch để kéo đúng torch==2.3.1+cpu như requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# 3) Copy source + dữ liệu + static
COPY . .
# đảm bảo có: /app/app.py, /app/data/profile.json, /app/static/cutechatbot.png

# 4) Env & expose
ENV PORT=8080 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
EXPOSE 8080

# 5) Healthcheck (khớp /health trong app)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fsS http://127.0.0.1:${PORT}/health || exit 1

# 6) Run (Koyeb sẽ set PORT thật khi chạy)
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","${PORT}"]
