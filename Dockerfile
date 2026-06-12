# TrendWear Cloud Platform — bitta Docker image
# Frontend + Backend BITTA portda (8000) ishlaydi
FROM python:3.11-slim

WORKDIR /code

# Tizim kutubxonalari (bcrypt/psycopg2 uchun)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

# Bog'liqliklarni o'rnatish (cache uchun alohida qatlam)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ilova kodi
COPY app/ ./app/

# SQLite ma'lumotlar bazasi uchun papka
RUN mkdir -p /data

# Bitta port — frontend ham, API ham shu yerda
EXPOSE 8000

# Load Balancer uchun health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Uvicorn server (production)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
