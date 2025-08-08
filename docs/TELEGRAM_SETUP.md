# Инструкция по подключению PhraseWeaver к Telegram

## 1. Создание Telegram бота

### Шаг 1: Создайте бота через BotFather
1. Откройте Telegram и найдите [@BotFather](https://t.me/botfather)
2. Отправьте команду `/newbot`
3. Введите имя для вашего бота (например: "PhraseWeaver")
4. Введите username для бота (например: "phraseweaver_bot")
5. Сохраните полученный **токен бота** - он понадобится позже

### Шаг 2: Настройте Web App
1. Отправьте BotFather команду `/mybots`
2. Выберите ваш бот
3. Выберите "Bot Settings" → "Menu Button" → "Configure Menu Button"
4. Введите текст кнопки (например: "Открыть PhraseWeaver")
5. Введите URL вашего Web App (см. раздел "Развертывание")

## 2. Настройка окружения

### Создайте файл .env в папке backend/
```bash
cd backend
touch .env
```

### Добавьте в .env следующие переменные:
```env
# Telegram Bot Settings
TELEGRAM_BOT_TOKEN=ваш_токен_бота_от_BotFather
TELEGRAM_WEBHOOK_URL=https://ваш_домен.com/api/telegram/webhook

# Security
SECRET_KEY=ваш_секретный_ключ_для_jwt

# Database (для продакшена)
DATABASE_URL=postgresql://user:password@localhost/phraseweaver

# CORS (для продакшена)
ALLOWED_ORIGINS=["https://ваш_домен.com"]

# External APIs (опционально)
OPENAI_API_KEY=ваш_openai_ключ
UNSPLASH_ACCESS_KEY=ваш_unsplash_ключ
```

## 3. Развертывание

### Вариант A: Локальное тестирование с ngrok

1. **Установите ngrok:**
   ```bash
   # macOS
   brew install ngrok
   
   # или скачайте с https://ngrok.com/
   ```

2. **Запустите backend сервер:**
   ```bash
   cd backend
   python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **В новом терминале запустите ngrok:**
   ```bash
   ngrok http 8000
   ```

4. **Скопируйте HTTPS URL из ngrok** (например: `https://abc123.ngrok.io`)

5. **Настройте frontend для продакшена:**
   - Отредактируйте `frontend/public/utils/api.js`
   - Измените `API_CONFIG.baseURL` на ваш ngrok URL:
   ```javascript
   const API_CONFIG = {
       baseURL: 'https://abc123.ngrok.io', // ваш ngrok URL
       timeout: 10000,
       headers: {
           'Content-Type': 'application/json'
       }
   };
   ```

6. **Разместите frontend файлы:**
   - Загрузите содержимое папки `frontend/public/` на любой веб-хостинг
   - Или используйте GitHub Pages, Netlify, Vercel

7. **Обновите настройки бота в BotFather:**
   - URL Web App должен указывать на ваш frontend (например: `https://username.github.io/phraseweaver`)

### Вариант B: Полное развертывание

1. **Backend развертывание:**
   - Heroku, Railway, DigitalOcean, AWS, etc.
   - Настройте PostgreSQL базу данных
   - Установите переменные окружения

2. **Frontend развертывание:**
   - GitHub Pages, Netlify, Vercel, Cloudflare Pages
   - Обновите API_CONFIG.baseURL на URL вашего backend

3. **Настройте HTTPS:**
   - Обязательно для Telegram Web Apps
   - Большинство хостингов предоставляют SSL автоматически

## 4. Настройка Telegram Web App

### В BotFather:
1. `/mybots` → выберите бота → "Bot Settings"
2. "Menu Button" → "Configure Menu Button"
3. Введите:
   - **Button text:** "🎓 Открыть PhraseWeaver"
   - **Web App URL:** URL вашего frontend приложения

### Дополнительные настройки:
1. **Описание бота:** `/setdescription`
2. **Аватар бота:** `/setuserpic`
3. **Команды бота:** `/setcommands`
   ```
   start - Запустить PhraseWeaver
   help - Помощь
   ```

## 5. Тестирование

### Локальное тестирование:
1. Убедитесь, что оба сервера запущены
2. Откройте http://localhost:3000 в браузере
3. Проверьте, что режим разработки работает

### Тестирование в Telegram:
1. Найдите вашего бота в Telegram
2. Нажмите "/start" или кнопку меню
3. Должно открыться ваше Web App
4. Проверьте аутентификацию и основные функции

## 6. Безопасность

### Важные моменты:
1. **Проверка подписи Telegram:** В продакшене обязательно включите проверку `initData`
2. **HTTPS:** Telegram Web Apps работают только по HTTPS
3. **CORS:** Настройте правильные домены в `ALLOWED_ORIGINS`
4. **Секретные ключи:** Никогда не коммитьте `.env` файлы в git

### Обновите backend для проверки подписи:
```python
# В backend/app/api/auth.py добавьте проверку initData
import hmac
import hashlib
from urllib.parse import parse_qsl

def verify_telegram_auth(init_data: str, bot_token: str) -> bool:
    """Проверка подписи Telegram WebApp"""
    try:
        parsed_data = dict(parse_qsl(init_data))
        hash_value = parsed_data.pop('hash', '')
        
        data_check_string = '\n'.join(
            f"{k}={v}" for k, v in sorted(parsed_data.items())
        )
        
        secret_key = hmac.new(
            "WebAppData".encode(), 
            bot_token.encode(), 
            hashlib.sha256
        ).digest()
        
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return calculated_hash == hash_value
    except Exception:
        return False
```

## 7. Полезные ссылки

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram Web Apps](https://core.telegram.org/bots/webapps)
- [BotFather](https://t.me/botfather)
- [ngrok](https://ngrok.com/)
- [Telegram Web Apps Examples](https://github.com/telegram-web-app)

## Поддержка

Если возникли проблемы:
1. Проверьте логи backend сервера
2. Откройте Developer Tools в браузере
3. Убедитесь, что все URL настроены правильно
4. Проверьте, что HTTPS работает корректно


URL для настройки Web App в Telegram боте зависит от способа развертывания:

1. Локальное тестирование с ngrok:

- Установите ngrok: brew install ngrok (macOS)
- Запустите: ngrok http 3000
- Получите HTTPS URL вида: https://abc123.ngrok.io
- Используйте этот URL в настройках бота
2. Развертывание на хостинге:

- Netlify/Vercel (для frontend): получите URL вида https://your-app.netlify.app
- Heroku/Railway (для fullstack): получите URL вида https://your-app.herokuapp.com
- GitHub Pages : https://username.github.io/repository-name
Важные требования для Telegram:

- ✅ URL должен быть HTTPS (обязательно!)
- ✅ Должен быть доступен из интернета
- ✅ Сертификат SSL должен быть валидным

Решение проблемы с ngrok аутентификацией 🔐

Для использования ngrok требуется регистрация и токен аутентификации 1 . Вот пошаговое решение:

1. Регистрация в ngrok:

- Перейдите на https://dashboard.ngrok.com/signup
- Создайте бесплатный аккаунт
- Подтвердите email
2. Получение authtoken:

- Войдите в панель управления ngrok
- Перейдите на https://dashboard.ngrok.com/get-started/your-authtoken
- Скопируйте ваш персональный токен
3. Установка токена:

```
ngrok config add-authtoken YOUR_TOKEN_HERE
```
4. Запуск ngrok:

```
ngrok http 3000
```
Альтернативные решения без регистрации:

1. LocalTunnel (бесплатно, без регистрации):

```
npm install -g localtunnel
lt --port 3000
```
2. Serveo (через SSH):

```
ssh -R 80:localhost:3000 serveo.net
```
3. Cloudflare Tunnel:

```
brew install cloudflared
cloudflared tunnel --url http://localhost:3000
```
Рекомендация: Для быстрого тестирования используйте LocalTunnel - он не требует регистрации и сразу даст вам HTTPS URL для настройки Telegram бота.

После получения публичного HTTPS URL используйте его в настройках Menu Button вашего Telegram бота! 🚀