#!/bin/bash
if [ -z "$1" ]; then
    echo "Использование: ./check-deployment.sh YOUR_DOMAIN"
    exit 1
fi

URL=$1

echo "🔍 Проверка деплоя на $URL..."

# Проверка основного эндпоинта
echo "Проверка главной страницы..."
curl -s -o /dev/null -w "%{http_code}" "$URL/" | grep -q "200" && echo "✅ Главная страница работает" || echo "❌ Ошибка главной страницы"

# Проверка API health
echo "Проверка API health..."
curl -s -o /dev/null -w "%{http_code}" "$URL/api/health" | grep -q "200" && echo "✅ API health работает" || echo "❌ Ошибка API health"

# Проверка аутентификации
echo "Проверка аутентификации..."
curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d '{"init_data":"test","user":{"id":123}}' "$URL/api/auth/telegram/verify" | grep -q "200" && echo "✅ Аутентификация работает" || echo "❌ Ошибка аутентификации"

echo "✅ Проверка завершена"