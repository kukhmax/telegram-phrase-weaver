📋 Детальная пошаговая инструкция по деплою
🎯 Вариант 1: Railway (Рекомендуется)

Подготовка:
bash# Установка Railway CLI
npm install -g @railway/cli

# Создание аккаунта на https://railway.app

Получение Telegram Bot Token:

Напишите @BotFather в Telegram
Команда /newbot
Введите название бота: PhraseWeaver Bot
Введите username: phraseweaver_yourname_bot
Сохраните токен!


Деплой:
bash# В папке проекта
railway login
railway init phraseweaver

# Установка переменных
railway variables set TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
railway variables set SECRET_KEY=$(openssl rand -hex 32)

# Добавление PostgreSQL
railway add postgresql

# Деплой
railway up

Получите URL:
bashrailway status
# Скопируйте Generated Domain


🎯 Вариант 2: Render.com

Подготовка:

Создайте аккаунт на https://render.com
Подключите GitHub репозиторий


Создание Web Service:

New → Web Service
Connect Repository: ваш репозиторий
Настройки:
Build Command: pip install -r backend/requirements.txt
Start Command: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT



Environment Variables:
TELEGRAM_BOT_TOKEN=your_bot_token
SECRET_KEY=your_secret_key_here
ENVIRONMENT=production

База данных:

Dashboard → Add PostgreSQL
Скопируйте DATABASE_URL в переменные окружения



🎯 Вариант 3: Fly.io

Подготовка:
bash# Установка Fly CLI
curl -L https://fly.io/install.sh | sh

Деплой:
bashflyctl auth login
flyctl launch --name phraseweaver

# Настройка секретов
flyctl secrets set TELEGRAM_BOT_TOKEN=your_token
flyctl secrets set SECRET_KEY=$(openssl rand -hex 32)

# База данных
flyctl postgres create --name phraseweaver-db
flyctl postgres attach phraseweaver-db

# Деплой
flyctl deploy



🤖 Создание Telegram Mini App
1. Настройка бота:
Напишите @BotFather:
/newbot
PhraseWeaver Learning Bot
phraseweaver_learn_bot

/mybots
[Выберите вашего бота]
Bot Settings
Menu Button
Configure Menu Button

Button text: Открыть PhraseWeaver
Web App URL: https://your-domain.railway.app
2. Тестирование:

Найдите вашего бота в Telegram
Нажмите /start
Нажмите кнопку "Открыть PhraseWeaver"
Приложение должно открыться в WebApp


❓ Готовы ли продолжить?
Вопросы для уточнения:

Какую платформу предпочитаете для деплоя: Railway, Render или Fly.io?
Есть ли у вас GitHub репозиторий для проекта?
Получили ли вы токен бота от @BotFather?
🚀