# backend/app/main.py

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

# Безопасные импорты с обработкой ошибок
try:
    from app.core.config import get_settings
    settings = get_settings()
except Exception as e:
    logging.error(f"Ошибка загрузки настроек: {e}")
    # Создаем заглушку для настроек
    class MockSettings:
        REDIS_URL = "redis://redis:6379/0"
        DATABASE_URL = "postgresql+asyncpg://phraseweaver:secure_password_123@db:5432/phraseweaver"
    settings = MockSettings()

# Импорты роутеров с обработкой ошибок
routers_to_include = []
try:
    from app.routers import auth
    routers_to_include.append(('auth', auth.router))
except Exception as e:
    logging.warning(f"Не удалось загрузить auth router: {e}")

try:
    from app.routers import cards
    routers_to_include.append(('cards', cards.router))
except Exception as e:
    logging.warning(f"Не удалось загрузить cards router: {e}")

try:
    from app.routers import decks
    routers_to_include.append(('decks', decks.router))
except Exception as e:
    logging.warning(f"Не удалось загрузить decks router: {e}")

try:
    from app.routers import training_stats
    routers_to_include.append(('training_stats', training_stats.router))
except Exception as e:
    logging.warning(f"Не удалось загрузить training_stats router: {e}")

try:
    from app.routers import telegram
    routers_to_include.append(('telegram', telegram.router))
except Exception as e:
    logging.warning(f"Не удалось загрузить telegram router: {e}")

try:
    from app.routers import tts
    routers_to_include.append(('tts', tts.router))
except Exception as e:
    logging.warning(f"Не удалось загрузить tts router: {e}")

logging.basicConfig(level=logging.INFO)
logging.info(f"Загружено роутеров: {len(routers_to_include)}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logging.info("🚀 Запуск PhraseWeaver API")
    
    # Инициализация Telegram webhook
    try:
        from app.services.telegram_bot import set_webhook
        await set_webhook()
        logging.info("✅ Telegram webhook установлен")
    except Exception as e:
        logging.error(f"❌ Ошибка установки Telegram webhook: {e}")
    
    yield
    # Shutdown
    logging.info("🛑 Остановка PhraseWeaver API")

app = FastAPI(
    title="PhraseWeaver API",
    description="API для изучения языков через Telegram Mini App",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS настройки - упрощенные для стабильности
allowed_origins = [
    "https://pw-new.club",
    "https://www.pw-new.club",
    "https://web.telegram.org",
    "https://telegram.org",
    "https://telegram.me",
    "https://t.me",
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "*"  # Разрешаем все для совместимости
]

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "Accept",
        "Origin",
        "User-Agent"
    ],
    expose_headers=["X-Request-ID"]
)



# Базовые роуты
@app.get("/")
def root():
    return {
        "message": "PhraseWeaver API работает", 
        "version": "1.0.0",
        "routers": len(routers_to_include),
        "status": "ok"
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "version": "1.0.0",
        "routers_loaded": [name for name, _ in routers_to_include]
    }

# Подключаем роутеры с обработкой ошибок
for router_name, router in routers_to_include:
    try:
        app.include_router(router)
        logging.info(f"✅ Роутер {router_name} подключен")
    except Exception as e:
        logging.error(f"❌ Ошибка подключения роутера {router_name}: {e}")

# Статические файлы
try:
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
    logging.info("✅ Статические файлы подключены")
except Exception as e:
    logging.warning(f"⚠️ Не удалось подключить статические файлы: {e}")

# Обслуживание frontend приложения
@app.get("/app")
async def frontend():
    try:
        return FileResponse("frontend/index.html")
    except Exception as e:
        logging.error(f"Ошибка загрузки frontend: {e}")
        return {"error": "Frontend недоступен", "message": str(e)}

# Fallback для SPA роутинга
@app.get("/{path:path}")
async def serve_spa(path: str):
    """Обслуживание SPA - все неизвестные пути перенаправляем на index.html"""
    try:
        # Проверяем, существует ли файл
        import os
        file_path = f"frontend/{path}"
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Если файл не найден, возвращаем index.html для SPA
        if os.path.exists("frontend/index.html"):
            return FileResponse("frontend/index.html")
        
        return {"error": "File not found", "path": path}
    except Exception as e:
        logging.error(f"Ошибка обслуживания SPA: {e}")
        return {"error": "SPA routing error", "message": str(e)}