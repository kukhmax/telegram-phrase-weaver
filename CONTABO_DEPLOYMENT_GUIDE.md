# 🚀 Полное руководство по переносу PhraseWeaver на сервер Contabo

*Пошаговая инструкция для обычных пользователей без технического опыта*

---


## 📋 Что мы будем делать?

Мы перенесем ваше приложение PhraseWeaver (изучение языков через Telegram) с текущего хостинга на более дешевый и надежный сервер Contabo. Это позволит:
- **Сэкономить деньги** (в 3-5 раз дешевле)
- **Получить больше контроля** над приложением
- **Избежать ограничений** текущего хостинга

---

## 🎯 Что вам понадобится?

### Обязательно:
- **Компьютер** с доступом в интернет
- **Банковская карта** для оплаты сервера (~€4-8/месяц)
- **2-3 часа свободного времени**
- **Терпение** - мы все сделаем пошагово!

### Желательно:
- **Домен** (например, myapp.com) - можно купить за €10/год
- **Базовые навыки** работы с компьютером

### 🎯 Можно запустить без домена:
Для Telegram бота достаточно использовать IP-адрес:

```
https://123.45.67.89/api/telegram/webhook
```
Для веб-приложения тоже можно использовать IP:

```
http://123.45.67.89
```
### 📋 Что нужно изменить в инструкции: 🔧 В настройке .env файла:
```
# Вместо домена используйте IP
API_BASE_URL=http://123.45.67.89
``` 🤖 В настройке webhook для бота:
```
curl -X POST "https://api.telegram.org/bot
[ВАШ_ТОКЕН_БОТА]/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "http://123.45.67.89/api/
     telegram/webhook"}'
```
### ⚠️ Важные моменты при использовании IP: 🔒 SSL сертификат:
- Без домена нельзя получить бесплатный SSL от Let's Encrypt
- Telegram webhook может работать по HTTP (не HTTPS)
- Веб-приложение будет доступно только по HTTP 🌐 Доступность:
- IP может измениться при перезагрузке сервера Contabo
- Нужно будет обновить webhook при смене IP
- Пользователям сложнее запомнить IP вместо домена
### 💡 Рекомендуемая стратегия: 🚀 Этап 1: Запуск с IP (сразу)
1. 1.
   Настроить сервер с IP-адресом
2. 2.
   Запустить приложение
3. 3.
   Протестировать бота в Telegram
4. 4.
   Убедиться что все работает 🌟 Этап 2: Добавить домен (позже)
1. 1.
   Купить домен когда будете готовы
2. 2.
   Настроить DNS на IP сервера
3. 3.
   Получить SSL сертификат
4. 4.
   Обновить webhook на новый домен
### 📊 Экономия без домена:
- Сервер Contabo: €5.36/месяц
- Домен: €0 (пока не покупаете)
- SSL: €0 (не нужен для HTTP)
- Итого: €5.36/месяц
Экономия €10/год на домене!

---

## 📚 Словарь терминов

**Сервер** - это компьютер в дата-центре, который работает 24/7 и на котором будет размещено ваше приложение.

**VPS** (Virtual Private Server) - виртуальный сервер, часть мощного физического сервера, выделенная только вам.

**SSH** - способ безопасного подключения к серверу через интернет (как удаленный рабочий стол, но через текст).

**Docker** - технология, которая упаковывает ваше приложение в "контейнеры" для легкого запуска на любом сервере.

**База данных** - место, где хранятся все данные вашего приложения (пользователи, карточки, прогресс).

**Домен** - красивый адрес вашего сайта (например, phraseweaver.com вместо 123.45.67.89).

---

# 🏁 ЭТАП 1: Регистрация и настройка сервера Contabo

## Шаг 1.1: Регистрация на Contabo

1. **Откройте сайт** [contabo.com](https://contabo.com)
2. **Нажмите "VPS"** в верхнем меню
3. **Выберите план:**
   - **Cloud VPS 10** (€5.36/месяц) - для начала хватит (3 CPU, 8GB RAM, 75GB NVMe)
   - **Или Cloud VPS 20** (€8.33/месяц) - если планируете много пользователей (6 CPU, 12GB RAM, 100GB NVMe)

4. **Настройте сервер:**
   - **Операционная система:** Ubuntu 22.04
   - **Регион:** Europe (ближайший к вам)
   - **Период:** 1 месяц (для начала)

5. **Заполните данные:**
   - Имя, фамилия, email, адрес
   - Придумайте пароль для аккаунта

6. **Оплатите** банковской картой

## Шаг 1.2: Получение данных сервера

1. **Проверьте email** - придет письмо с данными сервера:
   ```
   IP-адрес: 123.45.67.89
   Пользователь: root
   Пароль: сложный_пароль_123
   ```

2. **Сохраните эти данные** в надежном месте!

---

# 💻 ЭТАП 2: Подключение к серверу

## Шаг 2.1: Установка программы для подключения

### Для Windows:
1. **Скачайте PuTTY** с [putty.org](https://putty.org)
2. **Установите** как обычную программу

### Для Mac:
1. **Откройте Terminal** (Программы → Утилиты → Terminal)
2. Готово! Terminal уже установлен

### Для Linux:
1. **Откройте Terminal** (Ctrl+Alt+T)
2. Готово!

## Шаг 2.2: Первое подключение

### Для Windows (PuTTY):
1. **Запустите PuTTY**
2. **Введите IP-адрес** сервера в поле "Host Name"
3. **Нажмите "Open"**
4. **Введите логин:** root
5. **Введите пароль** (текст не будет виден - это нормально!)

### Для Mac/Linux (Terminal):
1. **Откройте Terminal**
2. **Введите команду:**
   ```bash
   ssh root@123.45.67.89
   ```
   (замените на ваш IP-адрес)
3. **Введите пароль** когда попросит

**🎉 Поздравляем! Вы подключились к серверу!**

---

# 🔧 ЭТАП 3: Настройка сервера

## Шаг 3.1: Обновление системы

**Скопируйте и вставьте** эти команды по одной:

```bash
# Обновляем список программ
apt update

# Устанавливаем обновления
apt upgrade -y
```

*Подождите 2-5 минут, пока все установится*

## Шаг 3.2: Установка Docker

**Docker** - это программа, которая запустит ваше приложение.

```bash
# Скачиваем и устанавливаем Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Устанавливаем Docker Compose (для управления несколькими контейнерами)
apt install docker-compose-plugin -y

# Устанавливаем Git (для скачивания кода)
apt install git -y
```

*Подождите 3-5 минут*

## Шаг 3.3: Создание пользователя (для безопасности)

```bash
# Создаем нового пользователя
adduser phraseweaver

# Добавляем его в группу Docker
usermod -aG docker phraseweaver

# Даем права администратора
usermod -aG sudo phraseweaver
```

**Введите пароль** для нового пользователя (запомните его!)

## Шаг 3.4: Переключение на нового пользователя

```bash
# Переключаемся на нового пользователя
su - phraseweaver
```

---

# 🔄 ВАЖНО: Различия архитектуры

## Fly.io vs Contabo

### 🌐 **На Fly.io (раньше):**
- **Backend:** Только Dockerfile с приложением
- **PostgreSQL:** Внешний сервис Fly.io
- **Redis:** Внешний сервис Fly.io
- **Frontend:** Статические файлы в backend контейнере

### 🏠 **На Contabo (теперь):**
- **Backend:** Контейнер с приложением
- **PostgreSQL:** Собственный контейнер
- **Redis:** Собственный контейнер
- **Frontend:** Отдельный Nginx контейнер
- **Сеть:** Все контейнеры в изолированной сети

### ✅ **Преимущества новой архитектуры:**
- **Полный контроль** над базой данных
- **Локальная сеть** между сервисами (быстрее)
- **Безопасность** - БД не доступна извне
- **Простота бэкапов** и миграций
- **Независимость** от внешних сервисов

---

# 📦 ЭТАП 4: Установка приложения

## Шаг 4.1: Скачивание кода приложения

```bash
# Скачиваем код приложения
git clone https://github.com/kukhmax/telegram-phrase-weaver.git

# Переходим в папку приложения
cd telegram-phrase-weaver
```

## Шаг 4.2: Настройка конфигурации

```bash
# Создаем файл с настройками
nano .env
```

**Откроется текстовый редактор.** Вставьте этот текст:

```env
# Настройки базы данных
DATABASE_URL=postgresql://phraseweaver:secure_password_123@db:5432/phraseweaver
POSTGRES_USER=phraseweaver
POSTGRES_PASSWORD=secure_password_123
POSTGRES_DB=phraseweaver

# Настройки Redis (кэш)
REDIS_URL=redis://redis:6379/0

# Токен вашего Telegram бота
TELEGRAM_BOT_TOKEN=ваш_токен_бота

# API ключи для сервисов
GOOGLE_API_KEY=ваш_google_api_ключ
UNSPLASH_ACCESS_KEY=ваш_unsplash_ключ
PEXELS_API_KEY=ваш_pexels_ключ

# Секретный ключ (придумайте сложный)
SECRET_KEY=очень_сложный_секретный_ключ_12345

# Адрес вашего сайта
API_BASE_URL=http://ваш-домен.com
```

**Сохраните файл:**
- Нажмите `Ctrl+X`
- Нажмите `Y`
- Нажмите `Enter`

---

# 🤖 ЭТАП 5: Настройка Telegram бота

## Шаг 5.1: Создание бота

1. **Откройте Telegram**
2. **Найдите @BotFather**
3. **Отправьте команду:** `/newbot`
4. **Введите имя бота:** PhraseWeaver Bot
5. **Введите username:** phraseweaver_bot (должен быть уникальным)
6. **Скопируйте токен** (длинная строка с цифрами и буквами)

## Шаг 5.2: Получение API ключей

### Google API (для переводов):
1. Идите на [console.cloud.google.com](https://console.cloud.google.com)
2. Создайте новый проект
3. Включите "Cloud Translation API"
4. Создайте API ключ

### Unsplash API (для картинок):
1. Идите на [unsplash.com/developers](https://unsplash.com/developers)
2. Зарегистрируйтесь
3. Создайте новое приложение
4. Скопируйте Access Key

### Pexels API (альтернатива для картинок):
1. Идите на [pexels.com/api](https://pexels.com/api)
2. Зарегистрируйтесь
3. Получите API ключ

## Шаг 5.3: Обновление конфигурации

```bash
# Редактируем файл настроек
nano .env
```

**Замените** все "ваш_токен" на реальные значения, которые вы получили.

---

# 🚀 ЭТАП 6: Запуск приложения

## Шаг 6.1: Сборка и запуск

```bash
# Собираем и запускаем все контейнеры для production
docker compose -f docker-compose.prod.yml up -d --build
```

*Подождите 5-10 минут, пока все скачается и запустится*

**Важно:** Мы используем `docker-compose.prod.yml` для production развертывания, который:
- Не открывает порты базы данных и Redis наружу (безопасность)
- Использует production режим без hot-reload
- Настроен для автоматического перезапуска контейнеров

## Шаг 6.2: Проверка работы

```bash
# Проверяем статус контейнеров
docker compose -f docker-compose.prod.yml ps
```

**Должно показать:**
```
NAME                    STATUS
telegram-phrase-weaver-backend-1    Up
telegram-phrase-weaver-db-1         Up
telegram-phrase-weaver-redis-1      Up
telegram-phrase-weaver-frontend-1   Up
```

## Шаг 6.3: Просмотр логов

```bash
# Смотрим логи приложения
docker compose -f docker-compose.prod.yml logs -f backend
```

**Нажмите Ctrl+C** чтобы выйти из просмотра логов.

---

# 🌐 ЭТАП 7: Настройка домена (опционально)

## Шаг 7.1: Покупка домена

1. **Идите на** [namecheap.com](https://namecheap.com) или [godaddy.com](https://godaddy.com)
2. **Найдите** свободный домен (например, myphraseweaver.com)
3. **Купите** домен (~€10/год)

## Шаг 7.2: Настройка DNS

1. **В панели управления доменом** найдите "DNS Settings"
2. **Создайте A-запись:**
   - **Имя:** @ (или оставьте пустым)
   - **Тип:** A
   - **Значение:** IP-адрес вашего сервера
   - **TTL:** 300

3. **Создайте CNAME-запись:**
   - **Имя:** www
   - **Тип:** CNAME
   - **Значение:** ваш-домен.com

*Подождите 1-24 часа, пока DNS обновится*

## Шаг 7.3: Установка SSL сертификата

### Вариант A: Let's Encrypt (бесплатно, рекомендуется)

```bash
# Устанавливаем Nginx
sudo apt install nginx -y

# Устанавливаем Certbot для SSL
sudo apt install certbot python3-certbot-nginx -y

# Получаем бесплатный SSL сертификат
sudo certbot --nginx -d ваш-домен.com -d www.ваш-домен.com
```

### Вариант B: SSL от Namecheap (платно)

#### Шаг 7.3.1: Активация SSL в Namecheap

1. **Войдите в панель Namecheap:**
   - Перейдите на [namecheap.com](https://namecheap.com)
   - Войдите в аккаунт
   - Перейдите в **SSL Certificates**

2. **Активируйте сертификат:**
   - Нажмите **Activate** рядом с вашим SSL
   - Выберите **"Manually"** в методах установки
   - Нажмите **Next**

#### Шаг 7.3.2: Создание CSR на сервере

```bash
# Создайте директорию для сертификатов
sudo mkdir -p /etc/ssl/ваш-домен
cd /etc/ssl/ваш-домен

# Создайте приватный ключ
sudo openssl genrsa -out private.key 2048

# Создайте CSR (Certificate Signing Request)
sudo openssl req -new -key private.key -out certificate.csr
```

**При создании CSR введите:**
- **Country Name:** RU (ваша страна)
- **State:** Moscow (ваш регион)
- **City:** Moscow (ваш город)
- **Organization:** PhraseWeaver
- **Organizational Unit:** IT Department
- **Common Name:** ваш-домен.com ⚠️ **ВАЖНО!**
- **Email:** ваш email
- **Challenge password:** оставьте пустым
- **Optional company name:** оставьте пустым

#### Шаг 7.3.3: Отправка CSR в Namecheap

```bash
# Скопируйте содержимое CSR
sudo cat certificate.csr
```

**Вставьте в форму Namecheap** весь текст включая:
```
-----BEGIN CERTIFICATE REQUEST-----
...
-----END CERTIFICATE REQUEST-----
```

#### Шаг 7.3.4: DNS валидация

1. **Выберите DNS валидацию** в Namecheap
2. **Добавьте CNAME запись** в DNS:
   - **Host:** предоставленный Namecheap
   - **Value:** предоставленный Namecheap
   - **TTL:** Automatic

3. **Дождитесь валидации** (5-30 минут)

#### Шаг 7.3.5: Получение и установка сертификата

**После валидации получите email с файлами:**
- `ваш-домен.crt` (основной сертификат)
- `ваш-домен.ca-bundle` (промежуточные сертификаты)

**Загрузите на сервер:**
```bash
# Объедините сертификаты
sudo cat ваш-домен.crt ваш-домен.ca-bundle > fullchain.pem

# Скопируйте в директорию
sudo cp fullchain.pem /etc/ssl/ваш-домен/
sudo cp private.key /etc/ssl/ваш-домен/

# Установите права доступа
sudo chmod 600 /etc/ssl/ваш-домен/private.key
sudo chmod 644 /etc/ssl/ваш-домен/fullchain.pem
```

#### Шаг 7.3.6: Обновление Nginx конфигурации

**Создайте новый nginx.conf:**
```nginx
# HTTP -> HTTPS редирект
server {
    listen 80;
    server_name ваш-домен.com www.ваш-домен.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS сервер
server {
    listen 443 ssl http2;
    server_name ваш-домен.com www.ваш-домен.com;

    # SSL сертификаты
    ssl_certificate /etc/ssl/ваш-домен/fullchain.pem;
    ssl_certificate_key /etc/ssl/ваш-домен/private.key;

    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Статические файлы фронтенда
    root /usr/share/nginx/html;
    index index.html;

    # Обработка фронтенда
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API проксирование на backend
    location /api/ {
        proxy_pass http://backend:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Шаг 7.3.7: Обновление docker-compose.prod.yml

**Добавьте монтирование SSL сертификатов:**
```yaml
frontend:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"  # Добавить HTTPS порт
  volumes:
    - ./backend/frontend:/usr/share/nginx/html:ro
    - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    - /etc/ssl:/etc/ssl:ro  # SSL сертификаты
  depends_on:
    - backend
  restart: unless-stopped
  networks:
    - app-network
```

---

# 📱 ЭТАП 8: Тестирование в Telegram

## Шаг 8.1: Настройка webhook

```bash
# Настраиваем webhook для Telegram бота
curl -X POST "https://api.telegram.org/bot[ВАШ_ТОКЕН_БОТА]/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://ваш-домен.com/api/telegram/webhook"}'
```

## Шаг 8.2: Тестирование бота

1. **Откройте Telegram**
2. **Найдите вашего бота** по username
3. **Отправьте команду:** `/start`
4. **Проверьте** что бот отвечает

## Шаг 8.3: Тестирование веб-приложения

1. **Откройте браузер**
2. **Перейдите на** https://ваш-домен.com
3. **Проверьте** что сайт загружается
4. **Протестируйте** создание колод и карточек

---

# 🔧 ЭТАП 9: Настройка автозапуска

## Шаг 9.1: Создание systemd сервиса

```bash
# Создаем сервис для автозапуска
sudo nano /etc/systemd/system/phraseweaver.service
```

**Вставьте этот текст:**

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

## Шаг 9.2: Активация автозапуска

```bash
# Перезагружаем systemd
sudo systemctl daemon-reload

# Включаем автозапуск
sudo systemctl enable phraseweaver

# Запускаем сервис
sudo systemctl start phraseweaver

# Проверяем статус
sudo systemctl status phraseweaver
```

---

# 📊 ЭТАП 10: Мониторинг и обслуживание

## Шаг 10.1: Полезные команды

```bash
# Просмотр логов
docker compose -f docker-compose.prod.yml logs -f

# Перезапуск приложения
docker compose -f docker-compose.prod.yml restart

# Остановка приложения
docker compose -f docker-compose.prod.yml down

# Запуск приложения
docker compose -f docker-compose.prod.yml up -d

# Обновление кода
git pull
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build

# Просмотр использования ресурсов
docker stats

# Очистка неиспользуемых данных
docker system prune -f
```

## Шаг 10.2: Резервное копирование

```bash
# Создание бэкапа базы данных
docker compose -f docker-compose.prod.yml exec db pg_dump -U phraseweaver phraseweaver > backup_$(date +%Y%m%d).sql

# Восстановление из бэкапа
docker compose -f docker-compose.prod.yml exec -T db psql -U phraseweaver phraseweaver < backup_20241219.sql
```

## Шаг 10.3: Обновление приложения

```bash
# Скачиваем новую версию
git pull

# Пересобираем контейнеры
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build

# Проверяем что все работает
docker compose -f docker-compose.prod.yml ps
```

---

# 🆘 РЕШЕНИЕ ПРОБЛЕМ

## Проблема: Контейнер не запускается

```bash
# Смотрим подробные логи
docker compose -f docker-compose.prod.yml logs имя_контейнера

# Проверяем конфигурацию
docker compose -f docker-compose.prod.yml config

# Пересобираем контейнер
docker compose -f docker-compose.prod.yml up -d --build имя_контейнера
```

## Проблема: Сайт не открывается

1. **Проверьте** что все контейнеры запущены: `docker compose -f docker-compose.prod.yml ps`
2. **Проверьте** настройки DNS домена (если используете)
3. **Проверьте** что порты открыты: `sudo ufw status`
4. **Проверьте** логи frontend: `docker compose -f docker-compose.prod.yml logs frontend`
5. **Проверьте** логи backend: `docker compose -f docker-compose.prod.yml logs backend`

## Проблема: Бот не отвечает

1. **Проверьте** токен бота в файле `.env`
2. **Проверьте** что webhook настроен правильно
3. **Проверьте** логи backend: `docker compose -f docker-compose.prod.yml logs backend`
4. **Перезапустите** приложение: `docker compose -f docker-compose.prod.yml restart`

## Проблема: База данных не работает

```bash
# Проверяем статус базы данных
docker compose -f docker-compose.prod.yml exec db psql -U phraseweaver -d phraseweaver -c "SELECT 1;"

# Пересоздаем базу данных (ВНИМАНИЕ: удалит все данные!)
docker compose -f docker-compose.prod.yml down
docker volume rm telegram-phrase-weaver_postgres_data
docker compose -f docker-compose.prod.yml up -d
```

---

# 💰 СТОИМОСТЬ И ЭКОНОМИЯ

## Ежемесячные расходы:

- **Сервер Contabo Cloud VPS 10:** €5.36/месяц
- **Домен:** €0.83/месяц (€10/год)
- **SSL сертификат:** Бесплатно (Let's Encrypt)
- **Итого:** ~€6.20/месяц

## Сравнение с Fly.io:

- **Fly.io:** $20-50/месяц
- **Contabo Cloud VPS 10:** €5.36/месяц (~$5.70)
- **Экономия:** $15-45/месяц (€13-40)

**За год экономия составит €150-480!**

---------------------------------------------------------------------
---------------------------------------------------------------------
---------------------------------------------------------------------

Конечно! Поздравляю с успешным завершением этого квеста. Вы проделали отличную работу.

Вот подробная инструкция в формате Markdown, которая описывает весь наш путь, включая все ошибки и их решения. Вы можете сохранить этот файл как `SSL_VALIDATION_GUIDE.md`.

---

# Пошаговое руководство: Установка SSL-сертификата Namecheap на сервер Contabo с Nginx в Docker

Это руководство описывает полный процесс валидации и установки SSL-сертификата от Namecheap на VPS-сервер Contabo, где сайт развернут с помощью Docker и Nginx в качестве веб-сервера. Мы рассмотрим самые частые ошибки и методы их решения.

## Общая проблема: "Курица и Яйцо"

Основная сложность заключается в том, что для получения SSL-сертификата нужен работающий веб-сервер, который может пройти проверку. Но для запуска веб-сервера с HTTPS-конфигурацией нужен уже полученный SSL-сертификат. Это создает замкнутый круг, который мы разорвем с помощью временной HTTP-конфигурации.

---

### Фаза 1: Первичная настройка и первая попытка валидации

Изначально Namecheap предлагает подтвердить домен через email, что не всегда возможно. Поэтому мы меняем метод на подтверждение через HTTP-файл.

1.  **Смена метода на Namecheap:** В панели управления SSL-сертификатом выберите "Edit Methods" и смените метод на **"Upload a validation file"** (HTTP-based validation).
2.  **Получение данных:** Namecheap предоставит вам:
    *   **Имя файла:** Например, `83D2C61FF05BBF77877CAD7D957C8DFA.txt`
    *   **Содержимое файла:** Длинная строка текста.
    *   **Путь для размещения:** `/.well-known/pki-validation/`
3.  **Создание файла на сервере:**
    ```bash
    # Создаем нужную структуру папок в директории, которая монтируется в /usr/share/nginx/html
    mkdir -p ./backend/frontend/.well-known/pki-validation/

    # Создаем файл с нужным содержимым
    echo "СОДЕРЖИМОЕ_ФАЙЛА" > ./backend/frontend/.well-known/pki-validation/ИМЯ_ФАЙЛА.txt
    ```

---

### Фаза 2: Устранение первой ошибки — Nginx не запускается

После добавления файла и попытки запустить Docker с полной HTTPS-конфигурацией, сайт не открывается.

#### **Ошибка №1: Контейнер Nginx постоянно перезапускается**

*   **Диагностика:**
    1.  Команда `docker ps` показывает для контейнера `frontend` статус **`Restarting`**.
    2.  Команда `docker-compose -f docker-compose.prod.yml logs frontend` показывает фатальную ошибку:
        > nginx: [emerg] cannot load certificate "/etc/ssl/pw-new-club/fullchain.pem": ... No such file or directory

*   **Причина:** `nginx.conf` содержит блок `listen 443 ssl` и требует файлы `ssl_certificate` и `ssl_certificate_key`, которых у нас еще нет, так как валидация не пройдена.

*   **Решение: Временная конфигурация Nginx.**
    Нужно **полностью заменить** содержимое `nginx.conf` на временную конфигурацию, которая работает **только по HTTP** и умеет отдавать файл для валидации.

    **`nginx.conf` (временный, для валидации):**
    ```nginx
    server {
        listen 80;
        server_name pw-new.club www.pw-new.club;

        # Обработка запросов для валидации SSL
        location /.well-known/pki-validation/ {
            root /usr/share/nginx/html;
        }

        # На все остальные запросы отвечаем ошибкой, чтобы не отдавать сайт по HTTP
        location / {
            return 404;
        }
    }
    ```
    После этого необходимо перезапустить Docker: `docker-compose -f docker-compose.prod.yml up -d --build`.

---

### Фаза 3: Проблема с утерянным приватным ключом

После успешной валидации мы выясняем, что у нас нет **приватного ключа (`.key`)**, который соответствует скачанному сертификату.

#### **Ошибка №2: Отсутствие файла `private.key`**

*   **Диагностика:** Мы не можем найти файл, который начинается с `-----BEGIN PRIVATE KEY-----` и соответствует нашему сертификату. **CSR-код — это не приватный ключ!**

*   **Причина:** Приватный ключ генерируется пользователем *до* запроса сертификата и никогда не передается центру сертификации. Если он утерян, скачанный сертификат бесполезен.

*   **Решение: Перевыпуск (Reissue) сертификата с новой парой "ключ-CSR".**
    1.  **Очистка:** Удалить все старые файлы из папки `ssl` на сервере: `rm *`.
    2.  **Генерация:** Создать на сервере новую пару "ключ+CSR":
        ```bash
        # Находясь в папке ssl
        openssl req -new -newkey rsa:2048 -nodes -keyout private.key -out pw-new.club.csr
        ```
        > **Важно:** При генерации на запрос `Common Name` нужно ввести точное имя домена: `pw-new.club`.
    3.  **Перевыпуск:** Скопировать содержимое нового CSR (`cat pw-new.club.csr`), зайти на Namecheap, выбрать "Reissue Certificate" и вставить этот CSR.
    4.  **Повторная валидация:** Заново пройти процедуру валидации через HTTP-файл с **новыми данными**, которые предоставит Namecheap.

---

### Фаза 4: Устранение ошибок в процессе повторной валидации и установки

#### **Ошибка №3: `ERR_CONNECTION_REFUSED` — ссылка на файл валидации не открывается**

*   **Диагностика:** Браузер не может подключиться к сайту по HTTP. `docker ps` снова показывает `Restarting` для Nginx.
*   **Причина:** Мы вернули **полную** конфигурацию в `nginx.conf` до того, как установили сертификат. Нужно снова использовать **временную** конфигурацию из Фазы 2.
*   **Решение:**
    1.  Вернуть во `nginx.conf` временный код (только с `listen 80`).
    2.  Перезапустить Docker.
    3.  Проверить доступность файла валидации в браузере.
    4.  **Дополнительная причина:** Проверить файрвол в панели управления Contabo. Убедиться, что для входящего трафика разрешены порты **TCP 80** и **TCP 443**.

#### **Ошибка №4: Docker-compose не запускается с ошибкой `KeyError: 'ContainerConfig'`**

*   **Диагностика:** При выполнении `docker-compose up` возникает длинная ошибка Python Traceback.
*   **Причина:** Внутренний сбой `docker-compose`, который не может корректно прочитать состояние запущенных контейнеров.
*   **Решение:** Полностью остановить и удалить контейнеры (данные в `volumes` сохранятся), а затем запустить заново.
    ```bash
    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml up -d
    ```

#### **Ошибка №5: Валидация долго висит в статусе `PENDING`, хотя ссылка открывается**

*   **Диагностика:** Технически все настроено верно, но Namecheap не меняет статус.
*   **Причина:** Неверное **содержимое** файла валидации. При каждой новой попытке перевыпуска Namecheap может генерировать новую строку для файла.
*   **Решение:** Связаться с поддержкой Namecheap, попросить их проверить. Они предоставят **актуальное содержимое**, которое нужно вставить в файл на сервере командой `echo "НОВОЕ_ПРАВИЛЬНОЕ_СОДЕРЖИМОЕ" > /путь/к/файлу.txt`.

---

### Фаза 5: Устранение ошибок на финальном этапе установки

После того как валидация пройдена и новый сертификат скачан.

#### **Ошибка №6: Команда `cat` выдает ошибку `No such file or directory`**

*   **Диагностика:** Невозможно объединить `.crt` и `.ca-bundle` файлы.
*   **Причина:** Опечатка в имени файла. Часто путают дефис (`-`) и нижнее подчеркивание (`_`).
*   **Решение:** Использовать `ls -la` в папке `ssl`, чтобы увидеть точные имена файлов и использовать их в команде `cat`.
    ```bash
    # Пример правильной команды
    cat pw-new_club.crt pw-new_club.ca-bundle > fullchain.pem
    ```

#### **Ошибка №7: После финальной настройки Nginx снова в статусе `Restarting`**

*   **Диагностика:** `docker ps` показывает `Restarting`. Логи (`docker-compose ... logs frontend`) показывают ошибку:
    > nginx: [emerg] ... PEM routines::bad end line

*   **Причина:** Файлы сертификатов при объединении "слиплись" без переноса строки (`-----END CERTIFICATE----------BEGIN CERTIFICATE-----`).
*   **Решение:** Пересоздать файл `fullchain.pem` более надежным способом, который гарантирует перенос строки между файлами.
    ```bash
    { cat pw-new_club.crt; echo; cat pw-new_club.ca-bundle; } > fullchain.pem
    ```

---

### Приложение: Финальные рабочие конфигурации

#### `docker-compose.prod.yml` (секция `frontend`)
```yaml
  frontend:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443" # <-- Важно добавить порт 443
    volumes:
      - ./backend/frontend:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./ssl:/etc/ssl/pw-new-club:ro # <-- Важно добавить том с сертификатами
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - app-network
```

#### `nginx.conf` (финальная версия)
```nginx
# Блок для HTTP (порт 80)
# Перенаправляет весь трафик на HTTPS
server {
    listen 80;
    server_name pw-new.club www.pw-new.club;
    return 301 https://$host$request_uri;
}

# Основной рабочий блок для HTTPS (порт 443)
server {
    listen 443 ssl http2;
    server_name pw-new.club www.pw-new.club;

    # Указываем пути к нашим сертификатам внутри контейнера
    ssl_certificate /etc/ssl/pw-new-club/fullchain.pem;
    ssl_certificate_key /etc/ssl/pw-new-club/private.key;

    # Все остальные настройки вашего сайта
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
