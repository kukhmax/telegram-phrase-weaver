import redis.asyncio as aioredis
from app.core.config import get_settings
import logging
from typing import Optional

settings = get_settings()

class RedisClient:
    """Wrapper для Redis клиента с обработкой ошибок подключения"""
    
    def __init__(self):
        self._client: Optional[aioredis.Redis] = None
        self._connection_failed = False
        
    async def _get_client(self) -> Optional[aioredis.Redis]:
        """Получить Redis клиент с проверкой подключения"""
        if self._connection_failed:
            return None
            
        if self._client is None:
            try:
                self._client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
                # Проверяем подключение
                await self._client.ping()
                logging.info("Redis connection established successfully")
            except Exception as e:
                logging.warning(f"Redis connection failed, proceeding without cache: {e}")
                self._connection_failed = True
                self._client = None
                
        return self._client
    
    async def get(self, key: str) -> Optional[str]:
        """Получить значение из Redis с обработкой ошибок"""
        client = await self._get_client()
        if client is None:
            return None
            
        try:
            return await client.get(key)
        except Exception as e:
            logging.warning(f"Redis GET failed for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Установить значение в Redis с обработкой ошибок"""
        client = await self._get_client()
        if client is None:
            return False
            
        try:
            await client.set(key, value, ex=ex)
            return True
        except Exception as e:
            logging.warning(f"Redis SET failed for key {key}: {e}")
            return False

# Создаем глобальный экземпляр
redis_client = RedisClient()