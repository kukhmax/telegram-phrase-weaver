#!/bin/bash

# Скрипт для принудительного обновления кода на сервере
# Решает проблемы с конфликтами слияния

echo "🔄 Принудительное обновление кода на сервере..."

# Остановка всех контейнеров
echo "⏹️  Остановка контейнеров..."
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# Показать статус git
echo "📊 Текущий статус git:"
git status

echo ""
echo "🗑️  Сброс всех локальных изменений..."

# Сброс индекса
git reset --hard

# Очистка неотслеживаемых файлов
git clean -fd

# Сброс к последнему коммиту
git reset --hard HEAD

# Принудительное получение обновлений
echo "📥 Получение обновлений из репозитория..."
git fetch origin

# Принудительное переключение на dev-branch
echo "🔄 Переключение на dev-branch..."
git checkout dev-branch

# Принудительное обновление до последней версии
echo "⬇️  Принудительное обновление..."
git reset --hard origin/dev-branch

# Проверка результата
echo "✅ Проверка обновления:"
git log --oneline -5

echo ""
echo "🔧 Проверка docker-compose.prod.yml:"
if [ -f "docker-compose.prod.yml" ]; then
    echo "✅ Файл docker-compose.prod.yml существует"
    docker-compose -f docker-compose.prod.yml config --quiet
    if [ $? -eq 0 ]; then
        echo "✅ YAML синтаксис корректен"
    else
        echo "❌ YAML содержит ошибки"
        exit 1
    fi
else
    echo "❌ Файл docker-compose.prod.yml не найден"
    exit 1
fi

echo ""
echo "🚀 Запуск деплоя..."
./deploy-fix.sh

echo "✅ Принудительное обновление завершено!"