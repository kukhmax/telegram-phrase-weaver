#!/bin/bash
echo "🚀 Деплой на Fly.io..."

if [ -z "$1" ]; then
    echo "Использование: ./deploy-fly.sh YOUR_BOT_TOKEN"
    exit 1
fi

# Проверка CLI Fly.io
if ! command -v flyctl &> /dev/null; then
    echo "Fly.io CLI не установлен. Установите: curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Инициализация приложения
flyctl auth login
flyctl launch --name phraseweaver --region fra

# Настройка секретов
flyctl secrets set TELEGRAM_BOT_TOKEN=$1
flyctl secrets set SECRET_KEY=$(openssl rand -hex 32)
flyctl secrets set ENVIRONMENT=production

# Добавление базы данных
flyctl postgres create --name phraseweaver-db --region fra

# Подключение к базе данных
flyctl postgres attach phraseweaver-db

# Деплой
flyctl deploy

echo "✅ Деплой завершен! URL: https://phraseweaver.fly.dev"
