#!/bin/bash
echo "🚀 Деплой на Railway..."

# Проверка CLI Railway
if ! command -v railway &> /dev/null; then
    echo "Railway CLI не установлен. Установите: npm install -g @railway/cli"
    exit 1
fi

# Логин в Railway
echo "Войдите в Railway:"
railway login

# Инициализация проекта
railway link

# Настройка переменных окружения
echo "Настройка переменных окружения..."
railway variables set TELEGRAM_BOT_TOKEN=$1
railway variables set SECRET_KEY=$(openssl rand -hex 32)
railway variables set ENVIRONMENT=production

# Добавление базы данных PostgreSQL
railway add postgresql

# Деплой
echo "Запуск деплоя..."
railway up

echo "✅ Деплой завершен! Проверьте URL в Railway Dashboard"
