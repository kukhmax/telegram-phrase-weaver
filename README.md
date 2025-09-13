# PhraseWeaver 🧠📚

**Telegram Mini App для изучения языков с использованием ИИ**

PhraseWeaver - это интеллектуальное приложение для изучения языков, которое использует искусственный интеллект для создания персонализированных карточек с фразами, изображениями и аудио. Приложение интегрируется с Telegram и предоставляет систему интервального повторения (SRS) для эффективного запоминания.

## ✨ Основные возможности

- 🤖 **ИИ-генерация фраз** с использованием Google Gemini
- 🎵 **Аудио произношение** с поддержкой TTS (Text-to-Speech)
- 🖼️ **Автоматический поиск изображений** для визуального запоминания
- 📊 **Система интервального повторения (SRS)** для оптимального обучения
- 🌍 **Поддержка множества языков**: английский, русский, французский, немецкий, испанский, польский, португальский
- 📱 **Telegram Mini App** - удобный доступ прямо из мессенджера
- 📈 **Статистика прогресса** и персональные настройки

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.12+
- Docker и Docker Compose
- Node.js 18+ (для разработки frontend)
- Git

### Системные требования

- **ОС**: Linux, macOS, Windows (с WSL2)
- **RAM**: минимум 2GB, рекомендуется 4GB
- **Диск**: минимум 5GB свободного места

## 📦 Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-username/telegram-phrase-weaver.git
cd telegram-phrase-weaver
```

### 2. Настройка окружения

```bash
# Создание виртуального окружения
python -m venv venv

# Активация (Linux/macOS)
source venv/bin/activate

# Активация (Windows)
venv\Scripts\activate

# Установка зависимостей
cd backend
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Создайте файл `.env` в корневой директории:

```bash
cp .env.example .env
```

Заполните необходимые переменные:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/phraseweaver
REDIS_URL=redis://localhost:6379

# AI Services
GOOGLE_API_KEY=your_gemini_api_key
PEXELS_API_KEY=your_pexels_api_key

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret

# Environment
ENVIRONMENT=development
DEBUG=true
```

### 4. Запуск с Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f backend
```

### 5. Инициализация базы данных

```bash
# Применение миграций
docker-compose exec backend alembic upgrade head

# Создание тестового пользователя (опционально)
docker-compose exec backend python -m app.scripts.create_test_user
```

## 🌐 Развертывание

### Развертывание на Render.com (рекомендуется)

#### 1. Подготовка к развертыванию

```bash
# Создание production ветки
git checkout -b production
git push origin production
```

#### 2. Настройка на Render.com

1. Зарегистрируйтесь на [render.com](https://render.com)
2. Подключите ваш GitHub репозиторий
3. Создайте новый **Web Service**:
   - **Environment**: Docker
   - **Branch**: production
   - **Build Command**: `docker build -t phraseweaver ./backend`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### 3. Настройка базы данных

1. Создайте **PostgreSQL** сервис на Render
2. Скопируйте `DATABASE_URL` из настроек
3. Создайте **Redis** сервис
4. Добавьте переменные окружения в Web Service

#### 4. Переменные окружения для production

```env
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
TELEGRAM_BOT_TOKEN=...
GOOGLE_API_KEY=...
PEXELS_API_KEY=...
```

### Развертывание на VPS

#### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Развертывание приложения

```bash
# Клонирование на сервер
git clone https://github.com/your-username/telegram-phrase-weaver.git
cd telegram-phrase-weaver

# Настройка production окружения
cp .env.example .env.production
# Отредактируйте .env.production

# Запуск в production режиме
docker-compose -f docker-compose.prod.yml up -d
```

#### 3. Настройка Nginx (опционально)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Развертывание на Contabo VPS (рекомендуется для экономии)

**Contabo** предоставляет мощные VPS серверы по очень доступным ценам (от €5.36/месяц), что делает его отличным выбором для развертывания PhraseWeaver.

#### Преимущества Contabo:
- 💰 **Низкая стоимость**: в 3-5 раз дешевле других провайдеров
- 🚀 **Высокая производительность**: NVMe SSD, мощные CPU
- 🌍 **Европейские дата-центры**: низкая задержка
- 🔧 **Полный root доступ**: полный контроль над сервером

#### 1. Регистрация и настройка сервера

1. **Перейдите на** [contabo.com](https://contabo.com)
2. **Выберите план:**
   - **Cloud VPS 10** (€5.36/месяц) - 3 CPU, 8GB RAM, 75GB NVMe
   - **Cloud VPS 20** (€8.33/месяц) - 6 CPU, 12GB RAM, 100GB NVMe
3. **Настройте сервер:**
   - **ОС**: Ubuntu 22.04 LTS
   - **Регион**: Europe (ближайший к вам)
   - **Период**: 1 месяц (для начала)
4. **Получите данные доступа** по email

#### 2. Подключение к серверу

```bash
# Подключение по SSH (замените IP на ваш)
ssh root@123.45.67.89

# При первом подключении введите пароль из email
```

#### 3. Настройка сервера

```bash
# Обновление системы
apt update && apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установка Docker Compose и Git
apt install docker-compose-plugin git -y

# Создание пользователя для безопасности
adduser phraseweaver
usermod -aG docker phraseweaver
usermod -aG sudo phraseweaver

# Переключение на нового пользователя
su - phraseweaver
```

#### 4. Развертывание приложения

```bash
# Клонирование репозитория
git clone https://github.com/your-username/telegram-phrase-weaver.git
cd telegram-phrase-weaver

# Создание конфигурации
cp .env.example .env
nano .env  # Отредактируйте настройки
```

**Пример конфигурации для Contabo:**

```env
# База данных (используем Docker контейнеры)
DATABASE_URL=postgresql://phraseweaver:secure_password_123@db:5432/phraseweaver
POSTGRES_USER=phraseweaver
POSTGRES_PASSWORD=secure_password_123
POSTGRES_DB=phraseweaver

# Redis
REDIS_URL=redis://redis:6379/0

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# AI Services
GOOGLE_API_KEY=your_gemini_api_key
PEXELS_API_KEY=your_pexels_api_key

# Security
SECRET_KEY=your_very_secure_secret_key

# Domain (используйте IP если нет домена)
API_BASE_URL=http://123.45.67.89
# или с доменом:
# API_BASE_URL=https://your-domain.com
```

#### 5. Запуск приложения

```bash
# Запуск в production режиме
docker compose -f docker-compose.prod.yml up -d --build

# Проверка статуса
docker compose -f docker-compose.prod.yml ps

# Просмотр логов
docker compose -f docker-compose.prod.yml logs -f
```

#### 6. Настройка домена и SSL (опционально)

**Если у вас есть домен:**

1. **Настройте DNS:**
   - Создайте A-запись: `@` → IP сервера
   - Создайте CNAME-запись: `www` → ваш домен

2. **Установите SSL сертификат:**

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получение бесплатного SSL
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

#### 7. Настройка автозапуска

```bash
# Создание systemd сервиса
sudo nano /etc/systemd/system/phraseweaver.service
```

**Содержимое файла:**

```ini
[Unit]
Description=PhraseWeaver Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
User=phraseweaver
WorkingDirectory=/home/phraseweaver/telegram-phrase-weaver
ExecStart=/usr/bin/docker compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
# Активация автозапуска
sudo systemctl daemon-reload
sudo systemctl enable phraseweaver
sudo systemctl start phraseweaver
```

#### 8. Настройка Telegram webhook

```bash
# Настройка webhook (замените токен и домен/IP)
curl -X POST "https://api.telegram.org/bot[YOUR_BOT_TOKEN]/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-domain.com/api/telegram/webhook"}'

# Или с IP адресом:
# -d '{"url": "http://123.45.67.89/api/telegram/webhook"}'
```

#### 9. Мониторинг и обслуживание

```bash
# Полезные команды для управления

# Просмотр статуса
docker compose -f docker-compose.prod.yml ps

# Перезапуск сервисов
docker compose -f docker-compose.prod.yml restart

# Обновление приложения
git pull
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build

# Резервное копирование БД
docker compose -f docker-compose.prod.yml exec db pg_dump -U phraseweaver phraseweaver > backup_$(date +%Y%m%d).sql

# Просмотр использования ресурсов
docker stats

# Очистка неиспользуемых данных
docker system prune -f
```

#### 💰 Стоимость Contabo vs другие провайдеры

| Провайдер | Конфигурация | Цена/месяц | Экономия |
|-----------|--------------|------------|----------|
| **Contabo Cloud VPS 10** | 3 CPU, 8GB RAM, 75GB NVMe | €5.36 | - |
| DigitalOcean | 2 CPU, 4GB RAM, 80GB SSD | $24 (~€22) | **€16.64** |
| AWS Lightsail | 2 CPU, 4GB RAM, 80GB SSD | $20 (~€18) | **€12.64** |
| Render.com | 1 CPU, 2GB RAM | $25 (~€23) | **€17.64** |

**Годовая экономия с Contabo: €150-200!**

#### 🔧 Решение проблем на Contabo

**Проблема: Контейнер не запускается**
```bash
# Проверка логов
docker compose -f docker-compose.prod.yml logs container_name

# Пересборка контейнера
docker compose -f docker-compose.prod.yml up -d --build container_name
```

**Проблема: Нет доступа к сайту**
```bash
# Проверка портов в файрволе Contabo
# Убедитесь что открыты порты 80 и 443 в панели управления

# Проверка статуса Nginx
docker compose -f docker-compose.prod.yml logs frontend
```

**Проблема: Бот не отвечает**
```bash
# Проверка webhook
curl "https://api.telegram.org/bot[YOUR_TOKEN]/getWebhookInfo"

# Проверка логов backend
docker compose -f docker-compose.prod.yml logs backend
```

> 📖 **Подробное руководство**: Полная инструкция по развертыванию на Contabo доступна в файле [CONTABO_DEPLOYMENT_GUIDE.md](./CONTABO_DEPLOYMENT_GUIDE.md)

## 💻 Использование

### Основные команды

```bash
# Запуск в режиме разработки
docker-compose up

# Перезапуск сервисов
docker-compose restart

# Остановка всех сервисов
docker-compose down

# Просмотр логов
docker-compose logs -f [service_name]

# Выполнение команд в контейнере
docker-compose exec backend bash

# Применение миграций
docker-compose exec backend alembic upgrade head

# Создание новой миграции
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### API Endpoints

#### Аутентификация
```http
POST /api/auth/telegram
Content-Type: application/json

{
  "init_data": "telegram_init_data_string"
}
```

#### Управление колодами
```http
# Получение списка колод
GET /api/decks/
Authorization: Bearer <token>

# Создание новой колоды
POST /api/decks/
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Английский для начинающих",
  "description": "Базовые фразы",
  "lang_from": "en",
  "lang_to": "ru"
}
```

#### Работа с карточками
```http
# Обогащение фразы ИИ
POST /api/cards/enrich
Content-Type: application/json
Authorization: Bearer <token>

{
  "phrase": "I learn English",
  "keyword": "learn",
  "lang_code": "en",
  "target_lang": "ru"
}

# Сохранение карточек
POST /api/cards/save
Content-Type: application/json
Authorization: Bearer <token>

{
  "deck_id": 1,
  "cards": [
    {
      "phrase": "I learn English",
      "translation": "Я изучаю английский",
      "keyword": "learn"
    }
  ]
}
```

### Работа с Telegram Bot

#### 1. Создание бота

1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Выполните команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните полученный токен

#### 2. Настройка Mini App

```bash
# Установка URL Mini App через BotFather
/setmenubutton
# Выберите вашего бота
# Введите URL: https://your-domain.com
```

## ⚙️ Конфигурация

### Настройка ИИ сервисов

#### Google Gemini API

1. Перейдите в [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Создайте новый API ключ
3. Добавьте ключ в переменную `GOOGLE_API_KEY`

#### Pexels API (для изображений)

1. Зарегистрируйтесь на [Pexels](https://www.pexels.com/api/)
2. Получите API ключ
3. Добавьте ключ в переменную `PEXELS_API_KEY`

### Настройка TTS (Text-to-Speech)

```python
# backend/app/core/config.py
class Settings:
    # TTS настройки
    TTS_PROVIDER = "gtts"  # или "edge-tts"
    TTS_LANGUAGE_MAPPING = {
        "en": "en-US",
        "ru": "ru-RU",
        "fr": "fr-FR",
        # ...
    }
```

### Настройка системы интервального повторения

```python
# backend/app/core/srs.py
SRS_INTERVALS = {
    "again": 1,      # 1 день
    "good": 2,       # 2 дня  
    "easy": 4        # 4 дня
}

EASE_FACTOR_DEFAULT = 2.5
EASE_FACTOR_MIN = 1.3
EASE_FACTOR_MAX = 3.0
```

### Настройка уведомлений

```python
# backend/app/core/scheduler.py
NOTIFICATION_SETTINGS = {
    "daily_reminder": {
        "enabled": True,
        "time": "09:00",  # UTC
        "message": "Время повторить карточки! 📚"
    },
    "streak_reminder": {
        "enabled": True,
        "days": [3, 7, 14, 30]  # напоминания о серии
    }
}
```

## 📋 Примеры использования

### Пример 1: Создание колоды для изучения английского

```python
# Создание колоды через API
import requests

headers = {"Authorization": "Bearer your_token"}
data = {
    "name": "Деловой английский",
    "description": "Фразы для офиса",
    "lang_from": "en",
    "lang_to": "ru"
}

response = requests.post(
    "http://localhost:8000/api/decks/",
    json=data,
    headers=headers
)

print(response.json())
# {"id": 1, "name": "Деловой английский", ...}
```

### Пример 2: Обогащение фразы с помощью ИИ

```python
# Генерация карточек с ИИ
data = {
    "phrase": "I have a meeting",
    "keyword": "meeting",
    "lang_code": "en",
    "target_lang": "ru"
}

response = requests.post(
    "http://localhost:8000/api/cards/enrich",
    json=data,
    headers=headers
)

result = response.json()
print(f"Сгенерировано {len(result['phrases'])} фраз")
for phrase in result['phrases']:
    print(f"📝 {phrase['original']} → {phrase['translation']}")
    print(f"🎵 Аудио: {phrase['audio_url']}")
    print(f"🖼️ Изображение: {phrase['image_url']}")
```

### Пример 3: Тренировка с системой SRS

```python
# Получение карточек для повторения
response = requests.get(
    "http://localhost:8000/api/training/due?deck_id=1",
    headers=headers
)

cards = response.json()
print(f"Карточек для повторения: {len(cards)}")

# Отправка ответа на карточку
for card in cards:
    print(f"Фраза: {card['phrase']}")
    user_answer = input("Ваш перевод: ")
    
    # Оценка ответа (again/good/easy)
    rating = "good" if user_answer.lower() == card['translation'].lower() else "again"
    
    requests.post(
        "http://localhost:8000/api/training/answer",
        json={"card_id": card['id'], "rating": rating},
        headers=headers
    )
```

### Пример 4: Интеграция с Telegram Bot

```python
# backend/app/services/telegram_service.py
from telegram import Bot

class TelegramService:
    def __init__(self, token: str):
        self.bot = Bot(token)
    
    async def send_daily_reminder(self, user_id: int, due_count: int):
        message = f"📚 У вас {due_count} карточек для повторения!\n\n"
        message += "Откройте PhraseWeaver для тренировки 🚀"
        
        await self.bot.send_message(
            chat_id=user_id,
            text=message,
            reply_markup={
                "inline_keyboard": [[
                    {"text": "🎯 Начать тренировку", "web_app": {"url": "https://your-domain.com"}}
                ]]
            }
        )
```

### Пример 5: Кастомизация ИИ промптов

```python
# backend/app/services/ai_service.py
CUSTOM_PROMPTS = {
    "business": {
        "system": "Ты помощник для изучения делового английского.",
        "user": "Создай 5 деловых фраз со словом '{keyword}' на уровне {level}"
    },
    "travel": {
        "system": "Ты помощник для изучения языка путешественников.",
        "user": "Создай 5 фраз для путешествий со словом '{keyword}'"
    }
}

# Использование кастомного промпта
ai_service = AIService()
result = ai_service.generate_phrases(
    phrase="I need a taxi",
    keyword="taxi",
    prompt_type="travel"
)
```

## 🔧 Разработка

### Структура проекта

```
telegram-phrase-weaver/
├── backend/                 # FastAPI приложение
│   ├── app/
│   │   ├── core/           # Конфигурация, настройки
│   │   ├── models/         # SQLAlchemy модели
│   │   ├── schemas/        # Pydantic схемы
│   │   ├── services/       # Бизнес-логика
│   │   ├── routers/        # API роуты
│   │   └── main.py         # Точка входа
│   ├── migrations/         # Alembic миграции
│   ├── assets/            # Статические файлы
│   └── requirements.txt    # Python зависимости
├── frontend/               # Telegram Mini App
│   ├── js/                # JavaScript логика
│   ├── css/               # Стили
│   └── index.html         # Главная страница
├── docker-compose.yml      # Локальная разработка
├── docker-compose.prod.yml # Production
└── README.md              # Документация
```

### Добавление новых языков

1. Обновите конфигурацию языков:

```python
# backend/app/core/config.py
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "flag": "🇺🇸", "tts_code": "en-US"},
    "ru": {"name": "Русский", "flag": "🇷🇺", "tts_code": "ru-RU"},
    "ja": {"name": "日本語", "flag": "🇯🇵", "tts_code": "ja-JP"},  # Новый язык
}
```

2. Добавьте в frontend:

```html
<!-- frontend/index.html -->
<option value="ja">🇯🇵 日本語</option>
```

3. Создайте миграцию для обновления существующих данных

### Добавление новых ИИ провайдеров

```python
# backend/app/services/ai_providers/openai_provider.py
from .base import BaseAIProvider

class OpenAIProvider(BaseAIProvider):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    async def generate_phrases(self, prompt: str) -> List[str]:
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return self.parse_response(response.choices[0].message.content)
```

## 🐛 Отладка и решение проблем

### Частые проблемы

#### 1. Ошибка подключения к базе данных

```bash
# Проверка статуса PostgreSQL
docker-compose ps postgres

# Просмотр логов
docker-compose logs postgres

# Перезапуск базы данных
docker-compose restart postgres
```

#### 2. Проблемы с ИИ API

```python
# Проверка API ключей
import os
from app.services.ai_service import AIService

ai_service = AIService()
try:
    result = ai_service.test_connection()
    print("✅ AI сервис работает")
except Exception as e:
    print(f"❌ Ошибка AI: {e}")
```

#### 3. Проблемы с TTS

```bash
# Проверка доступности TTS
curl -X POST "http://localhost:8000/api/cards/generate-audio" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "lang_code": "en"}'
```

### Логирование

```python
# backend/app/core/logging.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Мониторинг

```bash
# Проверка использования ресурсов
docker stats

# Проверка здоровья приложения
curl http://localhost:8000/health

# Мониторинг логов в реальном времени
docker-compose logs -f --tail=100
```

## 📚 Дополнительные ресурсы

- [Документация Telegram Bot API](https://core.telegram.org/bots/api)
- [Документация FastAPI](https://fastapi.tiangolo.com/)
- [Документация Google Gemini](https://ai.google.dev/docs)
- [Документация Pexels API](https://www.pexels.com/api/documentation/)
- [Руководство по Docker Compose](https://docs.docker.com/compose/)

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

## 📞 Поддержка

Если у вас есть вопросы или проблемы:

- 📧 Email: support@phraseweaver.com
- 💬 Telegram: [@phraseweaver_support](https://t.me/phraseweaver_support)
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/telegram-phrase-weaver/issues)

---

**Сделано с ❤️ для изучающих языки**