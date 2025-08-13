from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    TELEGRAM_BOT_TOKEN: str
    GOOGLE_API_KEY: str
    UNSPLASH_ACCESS_KEY: str
    SECRET_KEY: str
    API_BASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()