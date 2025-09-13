FROM python:3.11-slim

WORKDIR /app

# Копируем только папку backend, чтобы сохранить контекст чистым
COPY ./backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем только код бэкенда
COPY ./backend/ .

# Команда запуска
# Временно используем минимальную версию для диагностики
CMD ["python", "-m", "uvicorn", "app.main_minimal:app", "--host", "0.0.0.0", "--port", "8080"]