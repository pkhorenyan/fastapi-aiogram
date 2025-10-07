FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ../requirements.txt .
RUN pip install psycopg2
RUN pip install --no-cache-dir -r requirements.txt

COPY .. .

# Автопрогон миграций при старте
CMD ["/bin/sh", "-c", "alembic upgrade head && uvicorn api.main:app --host 0.0.0.0 --port 8000"]