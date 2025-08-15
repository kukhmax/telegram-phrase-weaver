#!/bin/bash

# Скрипт для очистки проекта от временных файлов Python

echo "🧹 Очистка проекта от кэша Python..."

# Найти и удалить все директории __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} +

# Найти и удалить все файлы .pyc
find . -type f -name "*.pyc" -delete

echo "✅ Проект успешно очищен!"
