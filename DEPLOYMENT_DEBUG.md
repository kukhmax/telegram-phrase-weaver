# Деплой PhraseWeaver на Fly.io - Полное руководство по отладке

## Обзор проекта

PhraseWeaver - это Telegram Mini App для изучения языков с использованием карточек и интервального повторения.

**Технологический стек:**
- Backend: FastAPI + Python
- База данных: PostgreSQL
- Кэш: Redis
- Деплой: Fly.io
- Контейнеризация: Docker

## Процесс деплоя и возникшие проблемы

### 1. Подготовка к деплою

#### Установка flyctl CLI
```bash
# Установка flyctl
brew install flyctl

# Авторизация
flyctl auth login
```

#### Проверка существующих приложений
```bash
# Просмотр всех приложений
flyctl apps list
```

**Результат:** Обнаружены приложения `phraseweaver` (suspended) и `p-w-db` (PostgreSQL база)

### 2. Настройка инфраструктуры

#### Создание Redis кластера
```bash
# Попытка создать Redis с именем p-w-redis
flyctl redis create
# ❌ Ошибка: имя уже занято

# Попытка с именем phraseweaver-redis
flyctl redis create
# ❌ Ошибка: имя уже занято

# Создание с уникальным именем
flyctl redis create pw-redis-$(date +%s)
# ✅ Успешно создан pw-redis-1755367064
```

#### Настройка секретов
```bash
# Добавление Redis URL в секреты
flyctl secrets set REDIS_URL="redis://default:password@pw-redis-1755367064.upstash.io"

# Просмотр всех секретов
flyctl secrets list
```

### 3. Исправление структуры проекта

#### Проблема: Циклические импорты
**Ошибка:** `ImportError` из-за циклических импортов между `app.db` и `app.models`

**Решение:** Создание отдельного файла `database.py`
```python
# backend/app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

# Lazy initialization для избежания проблем при импорте
def init_db():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return engine, async_session

Base = declarative_base()

async def get_db():
    engine, async_session = init_db()
    async with async_session() as session:
        yield session
```

#### Обновление зависимостей
```bash
# Добавление gunicorn для продакшена
echo "gunicorn" >> backend/requirements.txt
echo "greenlet" >> backend/requirements.txt
```

### 4. Проблемы с миграциями базы данных

#### Проблема 1: Отсутствие переменных окружения
**Ошибка:** `ValidationError` - отсутствуют переменные окружения

**Решение:** Создание `.env` файла и копирование в backend директорию
```bash
# Копирование .env файла
cp .env backend/.env
```

#### Проблема 2: Pydantic не принимает дополнительные поля
**Ошибка:** `ValidationError` - extra fields not permitted

**Решение:** Обновление конфигурации Pydantic
```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # ... поля настроек ...
    
    class Config:
        env_file = ".env"
        extra = 'ignore'  # Игнорировать дополнительные поля
```

#### Проблема 3: Отсутствие greenlet
**Ошибка:** `ValueError` - greenlet library required

**Решение:**
```bash
python3 -m pip install greenlet
```

#### Проблема 4: Asyncpg не найден в продакшене
**Ошибка:** `NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgres.asyncpg`

**Решение:** Создание простого скрипта для создания таблиц
```python
# backend/create_tables.py
import os
from sqlalchemy import create_engine, text

def create_tables():
    database_url = os.environ.get('DATABASE_URL')
    
    # Конвертация различных форматов URL
    if "postgresql+asyncpg://" in database_url:
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    elif "postgres+asyncpg://" in database_url:
        database_url = database_url.replace("postgres+asyncpg://", "postgresql://")
    elif "postgres://" in database_url:
        database_url = database_url.replace("postgres://", "postgresql://")
    
    engine = create_engine(database_url)
    
    # SQL команды для создания таблиц
    sql_commands = [
        # SQL для создания таблиц users, decks, cards
    ]
    
    with engine.connect() as conn:
        for sql in sql_commands:
            conn.execute(text(sql))
            conn.commit()
```

### 5. Настройка fly.toml

#### Обновление конфигурации деплоя
```toml
# fly.toml
app = 'phraseweaver'
primary_region = 'ams'

[build]
  dockerfile = "backend/Dockerfile"

[deploy]
release_command = "python create_tables.py"

[processes]
  app = "gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8080"

[[services]]
  protocol = "tcp"
  internal_port = 8080
  processes = ["app"]

  [[services.ports]]
    port = 80
    handlers = ["http"]
    force_https = true

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

[[vm]]
  memory = '1gb'
  cpu_kind = 'shared'
  cpus = 1
```

### 6. Проблемы с сетевой доступностью

#### Проблема: Отсутствие IP адресов
**Ошибка:** Приложение недоступно извне

**Диагностика:**
```bash
flyctl ips list
# Результат: пустой список
```

**Решение:**
```bash
# Выделение общего IPv4 адреса (бесплатно)
flyctl ips allocate-v4 --shared

# Выделение IPv6 адреса
flyctl ips allocate-v6

# Проверка
flyctl ips list
```

#### Проблема: Отсутствие HTTP сервисов
**Ошибка:** `flyctl services list` показывает пустой список

**Решение:** Добавление секции `[[services]]` в fly.toml (см. выше)

### 7. Проблемы с DNS

#### Проблема: ERR_NAME_NOT_RESOLVED
**Симптомы:**
- Браузер показывает "Service is unavailable"
- `curl: (6) Could not resolve host: phraseweaver.fly.dev`

**Диагностика:**
```bash
# Проверка DNS через внешний сервер
nslookup phraseweaver.fly.dev 8.8.8.8
# Результат: работает

# Проверка локального DNS
curl -I https://phraseweaver.fly.dev/health
# Ошибка: не может разрешить хост
```

**Временное решение:**
```bash
# Смена DNS серверов
sudo networksetup -setdnsservers Wi-Fi 8.8.8.8 8.8.4.4

# Очистка DNS кэша
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

**Постоянное решение:**
```bash
# Добавление записи в hosts файл
echo "66.241.125.110 phraseweaver.fly.dev" | sudo tee -a /etc/hosts
```

### 8. Финальная настройка API

#### Добавление корневого endpoint
```python
# backend/app/main.py
@app.get("/")
def root():
    return {
        "message": "PhraseWeaver API is running", 
        "version": "1.0.0", 
        "docs": "/docs"
    }
```

## Полезные команды для отладки

### Мониторинг приложения
```bash
# Статус приложения
flyctl status

# Просмотр логов
flyctl logs -n

# SSH подключение к контейнеру
flyctl ssh console

# Проверка сервисов
flyctl services list

# Проверка IP адресов
flyctl ips list
```

### Тестирование API
```bash
# Проверка health endpoint
curl https://phraseweaver.fly.dev/health

# Проверка главной страницы
curl https://phraseweaver.fly.dev/

# Проверка с verbose выводом
curl -v https://phraseweaver.fly.dev/health

# Проверка через IP (с правильным Host заголовком)
curl -H "Host: phraseweaver.fly.dev" https://66.241.125.110/health
```

### Работа с DNS
```bash
# Проверка DNS резолюции
nslookup phraseweaver.fly.dev
dig phraseweaver.fly.dev

# Проверка через внешний DNS
nslookup phraseweaver.fly.dev 8.8.8.8

# Ping IP адреса
ping 66.241.125.110
```

## Итоговая архитектура

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram      │    │   Fly.io         │    │   Databases     │
│   Mini App      │───▶│   phraseweaver   │───▶│                 │
│                 │    │   (2 machines)   │    │   PostgreSQL    │
└─────────────────┘    │   Load Balanced  │    │   Redis         │
                       └──────────────────┘    └─────────────────┘

Domains:
- phraseweaver.fly.dev (HTTPS)
- API docs: /docs
- Health check: /health

IP Addresses:
- IPv4: 66.241.125.110 (shared)
- IPv6: 2a09:8280:1::90:74c2:0
```

## Заключение

Основные проблемы при деплое:
1. **Циклические импорты** - решено созданием отдельного database.py
2. **Проблемы с asyncpg** - решено созданием простого скрипта миграций
3. **Отсутствие IP адресов** - решено выделением shared IPv4
4. **Отсутствие HTTP сервисов** - решено настройкой fly.toml
5. **DNS проблемы** - решено добавлением записи в hosts

Приложение успешно задеплоено и доступно по адресу: **https://phraseweaver.fly.dev**

### Полезные ссылки
- [Fly.io Documentation](https://fly.io/docs/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL on Fly.io](https://fly.io/docs/postgres/)