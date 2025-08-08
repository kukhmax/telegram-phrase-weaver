#!/bin/bash
echo "🧪 Локальное тестирование..."

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "Docker не установлен!"
    exit 1
fi

# Запуск локально
echo "Запуск локального сервера..."
docker-compose up --build

echo "✅ Приложение доступно на http://localhost:8000"
