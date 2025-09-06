# backend/app/main.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from alembic import command, config as alembic_config
from app.core.config import get_settings
from app.routers import auth, cards, decks, training_stats, telegram, tts
from app.middleware import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware
)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.notifications import send_daily_reminders  # TODO: implement
import logging

settings = get_settings()

logging.basicConfig(level=logging.INFO)

scheduler = AsyncIOScheduler()
scheduler.add_job(send_daily_reminders, 'interval', days=1)
scheduler.start()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run migrations on startup
    alembic_cfg = alembic_config.Config("alembic.ini")
    try:
        command.upgrade(alembic_cfg, "head")
    except Exception as e: 
        logging.error(f"Migration failed: {e}")
    yield  # App runs here
    # Optional shutdown logic

app = FastAPI(
    title="PhraseWeaver API",
    description="API для изучения языков через Telegram Mini App",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

# Определяем разрешенные origins в зависимости от окружения
if os.getenv("ENVIRONMENT") == "production":
    allowed_origins = [
        "https://pw-new.club",
        "https://www.pw-new.club",
        "https://web.telegram.org",
        "https://telegram.org",
        "https://telegram.me",
        "https://t.me",
        "tg://",
        "*"  # Telegram WebApp может использовать различные origins
    ]
else:
    # Для разработки разрешаем localhost
    allowed_origins = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1:8000",
        "https://pw-new.club",
        "https://www.pw-new.club",
        "https://web.telegram.org",
        "https://telegram.org",
        "*"  # Для разработки разрешаем все
    ]

# Добавляем middleware в правильном порядке (последний добавленный выполняется первым)

# 1. CORS middleware (должен быть последним)
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

# 2. Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# 3. Rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    calls=200,  # 200 запросов (увеличено для Telegram WebApp)
    period=60   # за 60 секунд
)

# 4. Request logging middleware (выполняется первым)
app.add_middleware(RequestLoggingMiddleware)



@app.get("/")
def root():
    return {"message": "PhraseWeaver API is running", "version": "1.0.0", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(auth.router)
app.include_router(cards.router)
app.include_router(decks.router)
app.include_router(training_stats.router)
app.include_router(telegram.router)
app.include_router(tts.router)

# Статические файлы фронтенда
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Главная страница фронтенда
@app.get("/app")
async def frontend():
    from fastapi.responses import FileResponse
    return FileResponse("frontend/index.html")