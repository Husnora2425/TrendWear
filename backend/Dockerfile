# TrendWear Backend — FastAPI REST API
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Tizim kutubxonalari (psycopg2 / bcrypt uchun)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

# Bog'liqliklar (cache qatlami)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ilova kodi
COPY app/ ./app/

# SQLite uchun papka (PostgreSQL ishlatilmasa)
RUN mkdir -p /data

EXPOSE 8001

# Load Balancer / Docker health-check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
