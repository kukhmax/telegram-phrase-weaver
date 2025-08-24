import redis.asyncio as aioredis
from app.core.config import get_settings  # Импорт настроек с REDIS_URL


settings = get_settings()  # Получаем настройки приложения
redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)  # decode для строк