#!/bin/bash

# Скрипт для исправления YAML файла на сервере

echo "🔍 Проверка docker-compose.prod.yml..."

# Проверяем синтаксис YAML
echo "📋 Содержимое файла вокруг строки 48:"
cat -n docker-compose.prod.yml | sed -n '45,55p'

echo ""
echo "🔧 Проверка синтаксиса YAML:"
docker-compose -f docker-compose.prod.yml config --quiet

if [ $? -eq 0 ]; then
    echo "✅ YAML файл корректен"
else
    echo "❌ YAML файл содержит ошибки"
    echo ""
    echo "🔄 Пересоздание файла из git..."
    git checkout HEAD -- docker-compose.prod.yml
    
    echo "📋 Проверка после восстановления:"
    docker-compose -f docker-compose.prod.yml config --quiet
    
    if [ $? -eq 0 ]; then
        echo "✅ Файл восстановлен успешно"
    else
        echo "❌ Проблема не решена, проверьте файл вручную"
        exit 1
    fi
fi

echo ""
echo "🚀 Запуск деплоя..."
./deploy-fix.sh