#!/bin/sh

# Выход из скрипта, если любая из команд завершится с ошибкой
set -e

# 1. Запуск миграций Alembic
echo "Running Alembic migrations..."
alembic upgrade head

# 2. Запуск веб-сервера Uvicorn
echo "Starting Uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000