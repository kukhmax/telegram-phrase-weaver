FROM python:3.12-slim

WORKDIR /app

# Копируем только папку backend, чтобы сохранить контекст чистым
COPY ./backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем только код бэкенда
COPY ./backend/ .

# Команда запуска
CMD gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8080