# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from alembic import command, config as alembic_config
from app.core.config import get_settings
from app.routers import auth, cards, decks

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

app = FastAPI(title="PhraseWeaver API")

origins = [
    "https://frontend-q7zq.onrender.com", # URL вашего фронтенда на Render
    # "http://localhost",
    # "http://localhost:8080", # Если вы вдруг запускаете фронтенд локально на другом порту
]


# CORS для Telegram Mini App (prod + local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В prod restrict to Telegram domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(auth.router)
app.include_router(cards.router)
app.include_router(decks.router)