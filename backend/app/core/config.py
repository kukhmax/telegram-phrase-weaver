# backend/app/core/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    TELEGRAM_BOT_TOKEN: str
    GOOGLE_API_KEY: str
    PEXELS_API_KEY: str
    SECRET_KEY: str
    API_BASE_URL: str

    class Config:
        env_file = "../.env"  # Путь к .env файлу в корневой директории проекта
        # Эта опция позволяет Pydantic не падать, если .env файл не найден
        # (что актуально для production, где мы используем переменные окружения)
        env_file_encoding = 'utf-8'
        extra = 'ignore'  # Игнорировать дополнительные поля

# Оборачиваем создание объекта Settings в функцию с кэшированием.
# Это значит, что Settings() будет создан только ОДИН раз при первом вызове,
# а все последующие вызовы будут возвращать уже созданный объект.
# Это "ленивая" загрузка.
@lru_cache()
def get_settings() -> Settings:
    return Settings()

