from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App settings
    app_name: str = "PhraseWeaver API"
    debug: bool = True
    version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"
    
    # Database
    database_url: str = "sqlite:///./phraseweaver.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Telegram
    telegram_bot_token: Optional[str] = None
    telegram_webhook_url: Optional[str] = None
    
    # External APIs (будем добавлять позже)
    openai_api_key: Optional[str] = None
    unsplash_access_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # CORS
    allowed_origins: list = ["*"]  # В продакшене ограничить
    
    # Supported languages
    supported_languages: dict = {
        'en': 'English',
        'ru': 'Русский', 
        'es': 'Español',
        'pt': 'Português',
        'pl': 'Polski',
        'de': 'Deutsch',
        'fr': 'Français',
        'it': 'Italiano'
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()