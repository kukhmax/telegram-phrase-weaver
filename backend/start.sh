#!/bin/sh
set -e

# Устанавливаем PYTHONPATH на текущую директорию (которая /app в контейнере)
# Это скажет Python'у и Alembic'у, что здесь нужно искать модули (например, папку 'app')
export PYTHONPATH=.

# Теперь Alembic сможет найти 'app.db' и 'app.core'
echo "Running Alembic migrations..."
alembic -c alembic.ini upgrade head

# Uvicorn'у это тоже не повредит
echo "Starting Uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000