# Multi-stage build для оптимизации размера образа
FROM python:3.11-slim as builder

WORKDIR /app

# Установка только build зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements и установка зависимостей
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --user -r /app/requirements.txt

# Runtime образ
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PYTHONPATH=/app \
    PYTHONHASHSEED=0 \
    MALLOC_ARENA_MAX=2 \
    OMP_NUM_THREADS=2

# Копируем установленные пакеты из builder
COPY --from=builder /root/.local /root/.local

# Копирование кода приложения
COPY . /app/RAG_API

# Создание директорий
RUN mkdir -p /app/RAG_API/uploads /app/RAG_API/chroma_db

# Убеждаемся, что локальные пакеты в PATH
ENV PATH=/root/.local/bin:$PATH

# Открываем порт
EXPOSE 8000

# Запуск приложения с оптимизированными параметрами
# Ограничения ресурсов применяются через docker-compose.yml или docker run --memory
CMD ["uvicorn", "RAG_API.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--limit-concurrency", "10", "--timeout-keep-alive", "5"]

