#!/bin/bash

# Скрипт для деплоя исправлений конфигурации

echo "🚀 Деплой исправлений конфигурации..."

# Остановка текущих контейнеров
echo "⏹️  Остановка контейнеров..."
docker-compose -f docker-compose.prod.yml down

# Пересборка и запуск с новой конфигурацией
echo "🔨 Пересборка и запуск контейнеров..."
docker-compose -f docker-compose.prod.yml up -d --build

# Проверка статуса
echo "📊 Проверка статуса контейнеров..."
docker-compose -f docker-compose.prod.yml ps

# Проверка логов nginx
echo "📋 Логи nginx:"
docker-compose -f docker-compose.prod.yml logs frontend

# Проверка логов backend
echo "📋 Логи backend:"
docker-compose -f docker-compose.prod.yml logs backend

echo "✅ Деплой завершен!"
echo "🌐 Проверьте сайт: https://pw-new.club"