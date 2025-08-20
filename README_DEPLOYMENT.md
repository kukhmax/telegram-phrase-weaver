# 🚀 PhraseWeaver - Развертывание на GitHub и Contabo

## 📋 Пошаговое руководство по развертыванию

### 1. 📤 Подготовка к публикации на GitHub

#### Шаг 1.1: Инициализация Git репозитория
```bash
# Перейдите в директорию проекта
cd /path/to/telegram-phrase-weaver

# Инициализируйте Git (если еще не сделано)
git init

# Добавьте все файлы
git add .

# Создайте первый коммит
git commit -m "Initial commit: PhraseWeaver application"
```

#### Шаг 1.2: Создание репозитория на GitHub
1. Зайдите на [GitHub.com](https://github.com)
2. Нажмите "New repository"
3. Назовите репозиторий: `telegram-phrase-weaver`
4. Сделайте репозиторий **приватным** (для безопасности)
5. НЕ добавляйте README, .gitignore или лицензию (они уже есть)
6. Нажмите "Create repository"

#### Шаг 1.3: Связывание с GitHub
```bash
# Добавьте удаленный репозиторий
git remote add origin https://github.com/YOUR_USERNAME/telegram-phrase-weaver.git

# Отправьте код на GitHub
git branch -M main
git push -u origin main
```

### 2. 🖥️ Подготовка сервера Contabo

#### Шаг 2.1: Заказ VPS на Contabo
1. Зайдите на [Contabo.com](https://contabo.com)
2. Выберите VPS S (4GB RAM, 50GB SSD) - достаточно для проекта
3. Выберите операционную систему: **Ubuntu 22.04 LTS**
4. Выберите дата-центр (рекомендуется европейский)
5. Оплатите заказ

#### Шаг 2.2: Получение доступа к серверу
После создания VPS вы получите:
- IP-адрес сервера
- Логин: `root`
- Пароль (в email)

### 3. 🔧 Настройка сервера

#### Шаг 3.1: Подключение к серверу
```bash
# Подключитесь по SSH (замените IP на ваш)
ssh root@YOUR_SERVER_IP
```

#### Шаг 3.2: Обновление системы
```bash
# Обновите пакеты
apt update && apt upgrade -y

# Установите необходимые пакеты
apt install -y git docker.io docker-compose-v2 nginx certbot python3-certbot-nginx

# Запустите Docker
systemctl start docker
systemctl enable docker
```

#### Шаг 3.3: Клонирование проекта
```bash
# Клонируйте ваш репозиторий
git clone https://github.com/YOUR_USERNAME/telegram-phrase-weaver.git
cd telegram-phrase-weaver
```

### 4. ⚙️ Настройка переменных окружения

#### Шаг 4.1: Создание .env файла
```bash
# Скопируйте шаблон
cp .env.example .env

# Отредактируйте файл
nano .env
```

#### Шаг 4.2: Заполните переменные окружения
```env
# Database configuration
DATABASE_URL=postgresql://phraseweaver:SECURE_PASSWORD@db:5432/phraseweaver

# API Keys
PEXELS_API_KEY=ваш_ключ_pexels
GOOGLE_API_KEY=ваш_ключ_google_ai
UNSPLASH_ACCESS_KEY=ваш_ключ_unsplash
TELEGRAM_BOT_TOKEN=ваш_токен_бота

# Security
SECRET_KEY=сгенерированный_секретный_ключ

# Redis configuration
REDIS_URL=redis://redis:6379

# API base URL (замените на ваш IP или домен)
API_BASE_URL=https://pw-new.club

# PostgreSQL configuration
POSTGRES_USER=phraseweaver
POSTGRES_PASSWORD=SECURE_PASSWORD
POSTGRES_DB=phraseweaver
```

### 5. 🐳 Запуск приложения

#### Шаг 5.1: Сборка и запуск контейнеров
```bash
# Запустите приложение в продакшн режиме
docker compose -f docker-compose.prod.yml up -d --build

# Проверьте статус контейнеров
docker compose -f docker-compose.prod.yml ps
```

#### Шаг 5.2: Выполнение миграций базы данных
```bash
# Выполните миграции
docker compose -f docker-compose.prod.yml exec backend python -m alembic upgrade head
```

### 6. 🌐 Настройка домена (опционально)

#### Если у вас есть домен:
```bash
# Настройте SSL сертификат
certbot --nginx -d pw-new.club -d www.pw-new.club

# Обновите nginx конфигурацию для HTTPS
```

### 7. 🤖 Настройка Telegram бота

#### Шаг 7.1: Установка webhook
```bash
# Замените YOUR_BOT_TOKEN и YOUR_DOMAIN/IP
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://pw-new.club/api/telegram/webhook"}'
```

### 8. ✅ Проверка работоспособности

#### Шаг 8.1: Тестирование
1. Откройте браузер и перейдите на `https://pw-new.club`
2. Проверьте работу Telegram бота
3. Убедитесь, что все функции работают

#### Шаг 8.2: Мониторинг логов
```bash
# Просмотр логов приложения
docker compose -f docker-compose.prod.yml logs -f backend

# Просмотр логов всех сервисов
docker compose -f docker-compose.prod.yml logs -f
```

## 🔧 Полезные команды

### Управление приложением
```bash
# Остановка приложения
docker compose -f docker-compose.prod.yml down

# Перезапуск приложения
docker compose -f docker-compose.prod.yml restart

# Обновление кода
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

### Резервное копирование
```bash
# Создание бэкапа базы данных
docker compose -f docker-compose.prod.yml exec db pg_dump -U phraseweaver phraseweaver > backup.sql

# Восстановление из бэкапа
docker compose -f docker-compose.prod.yml exec -T db psql -U phraseweaver phraseweaver < backup.sql
```

## 🚨 Важные замечания

1. **Безопасность**: Никогда не коммитьте .env файл с реальными ключами
2. **Бэкапы**: Регулярно создавайте резервные копии базы данных
3. **Обновления**: Регулярно обновляйте систему и Docker образы
4. **Мониторинг**: Следите за логами и производительностью

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи: `docker compose -f docker-compose.prod.yml logs`
2. Убедитесь, что все переменные окружения заполнены
3. Проверьте статус контейнеров: `docker compose -f docker-compose.prod.yml ps`

---

**Готово!** Ваше приложение PhraseWeaver теперь работает на сервере Contabo! 🎉