FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PYTHONPATH=/app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements и установка зависимостей
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копирование кода приложения
COPY . /app/RAG_API

# Создание директорий
RUN mkdir -p /app/RAG_API/uploads /app/RAG_API/chroma_db

# Открываем порт
EXPOSE 8000

# Запуск приложения
CMD ["uvicorn", "RAG_API.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

