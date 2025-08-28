# backend/app/middleware.py
"""
Middleware для безопасности и rate limiting.
"""

import time
import redis
from typing import Dict, Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .core.config import get_settings

settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis for storage.
    Implements sliding window rate limiting.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        calls: int = 100,  # Количество запросов
        period: int = 60,  # Период в секундах
        redis_url: Optional[str] = None
    ):
        super().__init__(app)
        self.calls = calls
        self.period = period
        
        # Инициализируем Redis клиент
        try:
            import redis.asyncio as aioredis
            self.redis = aioredis.from_url(
                redis_url or settings.REDIS_URL,
                decode_responses=True
            )
        except Exception:
            # Fallback к in-memory storage если Redis недоступен
            self.redis = None
            self._memory_storage: Dict[str, list] = {}
    
    async def dispatch(self, request: Request, call_next):
        # Получаем идентификатор клиента
        client_id = self._get_client_id(request)
        
        # Проверяем rate limit
        if not await self._check_rate_limit(client_id):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded. Max {self.calls} requests per {self.period} seconds.",
                    "retry_after": self.period
                },
                headers={"Retry-After": str(self.period)}
            )
        
        # Записываем запрос
        await self._record_request(client_id)
        
        # Продолжаем обработку запроса
        response = await call_next(request)
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """
        Получает идентификатор клиента для rate limiting.
        Использует IP адрес или user_id из токена.
        """
        # Пытаемся получить user_id из заголовка Authorization
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from .services.auth_service import auth_service
                token = auth_header.split(" ")[1]
                payload = auth_service.verify_access_token(token)
                user_id = payload.get("sub")
                if user_id:
                    return f"user:{user_id}"
            except Exception:
                pass
        
        # Fallback к IP адресу
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    async def _check_rate_limit(self, client_id: str) -> bool:
        """
        Проверяет, не превышен ли rate limit для клиента.
        """
        current_time = time.time()
        window_start = current_time - self.period
        
        if self.redis:
            # Используем Redis для хранения
            key = f"rate_limit:{client_id}"
            
            # Удаляем старые записи
            await self.redis.zremrangebyscore(key, 0, window_start)
            
            # Считаем текущие запросы
            current_requests = await self.redis.zcard(key)
            
            return current_requests < self.calls
        else:
            # Используем in-memory storage
            if client_id not in self._memory_storage:
                self._memory_storage[client_id] = []
            
            # Удаляем старые записи
            self._memory_storage[client_id] = [
                timestamp for timestamp in self._memory_storage[client_id]
                if timestamp > window_start
            ]
            
            return len(self._memory_storage[client_id]) < self.calls
    
    async def _record_request(self, client_id: str):
        """
        Записывает новый запрос для клиента.
        """
        current_time = time.time()
        
        if self.redis:
            # Используем Redis
            key = f"rate_limit:{client_id}"
            await self.redis.zadd(key, {str(current_time): current_time})
            await self.redis.expire(key, self.period + 1)
        else:
            # Используем in-memory storage
            if client_id not in self._memory_storage:
                self._memory_storage[client_id] = []
            
            self._memory_storage[client_id].append(current_time)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware для добавления заголовков безопасности.
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Добавляем заголовки безопасности
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy для дополнительной защиты
        if request.url.path.startswith("/static/") or request.url.path == "/app":
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://telegram.org; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://api.telegram.org;"
            )
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования запросов.
    """
    
    async def dispatch(self, request: Request, call_next):
        import logging
        import uuid
        
        # Генерируем уникальный ID для запроса
        request_id = str(uuid.uuid4())[:8]
        
        # Логируем входящий запрос
        logger = logging.getLogger("api.requests")
        start_time = time.time()
        
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Client: {client_ip} - User-Agent: {request.headers.get('User-Agent', 'unknown')}"
        )
        
        # Обрабатываем запрос
        try:
            response = await call_next(request)
            
            # Логируем ответ
            process_time = time.time() - start_time
            logger.info(
                f"[{request_id}] Response: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            # Логируем ошибки
            process_time = time.time() - start_time
            logger.error(
                f"[{request_id}] Error: {str(e)} - Time: {process_time:.3f}s"
            )
            raise