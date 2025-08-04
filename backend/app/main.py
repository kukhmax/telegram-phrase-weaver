from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import engine, Base
from .core.logging_config import setup_logging
from .api import auth, decks, cards

# Настраиваем логирование
setup_logging()

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Создаем приложение FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # Явно указываем frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(decks.router, prefix="/api/decks", tags=["decks"])
app.include_router(cards.router, prefix="/api/cards", tags=["cards"])

# Базовый endpoint для проверки
@app.get("/")
async def root():
    return {
        "message": "PhraseWeaver API работает!",
        "version": settings.version,
        "status": "ok"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.version
    }

# Health check endpoint для API
@app.get("/api/health")
async def api_health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.version
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)