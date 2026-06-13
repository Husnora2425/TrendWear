# TrendWear — Bitta konteynerda (nginx + FastAPI + SQLite)
# Ishga tushirish: docker build -t trendwear . && docker run -p 8000:8000 trendwear
#
# Bu Dockerfile docker-compose ishlatmasdan, bitta portda ishlatish uchun.
# PostgreSQL o'rniga SQLite ishlatiladi (ma'lumotlar /data ichida saqlanadi).

FROM python:3.11-slim AS backend-builder

WORKDIR /app
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl nginx && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app/ ./app/

# ---- Frontend fayllarini nginx joyiga ko'chirish ----
COPY frontend/html/ /usr/share/nginx/html/
COPY nginx-single.conf /etc/nginx/conf.d/default.conf

# SQLite uchun papka
RUN mkdir -p /data

# supervisord — nginx va uvicorn ni birgalikda boshqaradi
RUN pip install --no-cache-dir supervisor

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["/usr/local/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
