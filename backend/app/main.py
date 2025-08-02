from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import engine, Base
from .api import auth

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
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)