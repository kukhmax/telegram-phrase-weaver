#!/bin/bash

# Скрипт для остановки серверов PhraseWeaver
echo "⏹️ Остановка серверов PhraseWeaver..."

# Остановка backend сервера
echo "🔧 Остановка backend сервера..."
pkill -f "uvicorn.*app.main:app" && echo "✅ Backend остановлен" || echo "ℹ️ Backend не был запущен"

# Остановка frontend сервера
echo "🌐 Остановка frontend сервера..."
pkill -f "python.*http.server.*3000" && echo "✅ Frontend остановлен" || echo "ℹ️ Frontend не был запущен"

echo "✅ Все серверы остановлены!"