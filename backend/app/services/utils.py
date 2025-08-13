import redis.asyncio as aioredis
from app.core.config import settings  # Импорт настроек с REDIS_URL

redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)  # decode для строк