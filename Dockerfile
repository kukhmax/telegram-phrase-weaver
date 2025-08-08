# 1. Dockerfile (в корне проекта)
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements.txt и установка Python зависимостей
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Создание директории для логов
RUN mkdir -p /app/logs

# Открытие порта
EXPOSE 8000

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Запуск приложения
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]