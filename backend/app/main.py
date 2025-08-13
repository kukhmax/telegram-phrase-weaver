from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import router

app = FastAPI(title="PhraseWeaver API")

# CORS для Telegram Mini App (prod + local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В prod restrict to Telegram domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Позже добавим routers