from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import structlog
import redis
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.database import engine, SessionLocal
import os

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer() if settings.ENVIRONMENT == "development" else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(30),  # INFO level
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Lifespan manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting PhraseWeaver Telegram Mini App")
    
    # Test database connection
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("Database connection successful")
    except Exception as e:
        logger.error("Database connection failed", error=str(e))
        raise
    
    # Test Redis connection
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        logger.info("Redis connection successful")
    except Exception as e:
        logger.error("Redis connection failed", error=str(e))
        raise
    
    # Create uploads directory
    os.makedirs("uploads/audio", exist_ok=True)
    os.makedirs("uploads/images", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    yield
    
    # Shutdown
    logger.info("Shutting down PhraseWeaver")

# Create FastAPI app
app = FastAPI(
    title="PhraseWeaver API",
    description="Telegram Mini App for language learning with AI-powered content generation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware configuration for Telegram WebApp
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://web.telegram.org",
        "https://k.web.telegram.org",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="uploads"), name="static")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        db_status = "unhealthy"
    
    try:
        # Check Redis
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        redis_status = "healthy"
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        redis_status = "unhealthy"
    
    status = "healthy" if db_status == "healthy" and redis_status == "healthy" else "unhealthy"
    
    return {
        "status": status,
        "components": {
            "database": db_status,
            "redis": redis_status
        },
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PhraseWeaver API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Basic API endpoint for testing
@app.get("/api/test")
async def test_api():
    """Test API endpoint"""
    logger.info("Test API endpoint called")
    return {
        "message": "API is working correctly",
        "environment": settings.ENVIRONMENT,
        "database_connected": True,
        "redis_connected": True
    }

# Telegram webhook endpoint placeholder
@app.post("/webhook/telegram")
async def telegram_webhook():
    """Telegram webhook endpoint (placeholder)"""
    return {"status": "received"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )