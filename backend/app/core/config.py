from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "PhraseWeaver"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/phraseweaver"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_WEBAPP_URL: Optional[str] = None
    
    # AI Services
    GOOGLE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # External APIs
    UNSPLASH_ACCESS_KEY: Optional[str] = None
    PIXABAY_API_KEY: Optional[str] = None
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Supported Languages
    SUPPORTED_LANGUAGES: dict = {
        'en': 'English',
        'es': 'Español',
        'pt': 'Português',
        'ru': 'Русский',
        'pl': 'Polski',
        'de': 'Deutsch',
        'fr': 'Français',
        'it': 'Italiano',
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()