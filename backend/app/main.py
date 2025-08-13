from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from alembic import command, config as alembic_config
from app.core.config import settings
from app.routers import cards

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.notifications import send_daily_reminders  # TODO: implement

scheduler = AsyncIOScheduler()
scheduler.add_job(send_daily_reminders, 'interval', days=1)
scheduler.start()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run migrations on startup
    alembic_cfg = alembic_config.Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    yield  # App runs here
    # Optional shutdown logic

app = FastAPI(title="PhraseWeaver API")

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

app.include_router(cards.router)