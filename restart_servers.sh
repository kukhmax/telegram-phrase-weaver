#!/bin/bash

# Скрипт для перезапуска серверов PhraseWeaver
echo "🔄 Перезапуск серверов PhraseWeaver..."

# Остановка существующих процессов
echo "⏹️ Остановка существующих серверов..."
pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
pkill -f "python.*http.server.*3000" 2>/dev/null || true

# Ждем завершения процессов
sleep 2

# Переход в директорию проекта
cd "$(dirname "$0")"

echo "🚀 Запуск backend сервера..."
# Запуск backend в фоне
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "🌐 Запуск frontend сервера..."
# Запуск frontend в фоне
cd frontend/public && python3 -m http.server 3000 &
FRONTEND_PID=$!

# Возврат в корневую директорию
cd ../..

echo "✅ Серверы запущены!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "💡 Для остановки серверов используйте: ./stop_servers.sh"
echo "📝 Логи AI сервиса: backend/logs/ai_service.log"
echo "📋 Общие логи: backend/logs/app.log"