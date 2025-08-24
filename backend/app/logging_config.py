# backend/app/logging_config.py
"""
Конфигурация логирования для приложения.
"""

import logging
import logging.config
import os
from typing import Dict, Any


def get_logging_config() -> Dict[str, Any]:
    """
    Возвращает конфигурацию логирования.
    
    Returns:
        Dict: Конфигурация для logging.config.dictConfig
    """
    
    # Определяем уровень логирования в зависимости от окружения
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Определяем формат логов
    detailed_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "%(filename)s:%(lineno)d - %(funcName)s() - %(message)s"
    )
    
    simple_format = "%(asctime)s - %(levelname)s - %(message)s"
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": detailed_format,
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": simple_format,
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(filename)s %(lineno)d %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "simple",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            },
            "api_requests": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "simple",
                "filename": "logs/api_requests.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10,
                "encoding": "utf8"
            }
        },
        "loggers": {
            # Корневой логгер
            "": {
                "level": log_level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False
            },
            # Логгер для API запросов
            "api.requests": {
                "level": "INFO",
                "handlers": ["api_requests", "console"],
                "propagate": False
            },
            # Логгер для приложения
            "app": {
                "level": log_level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False
            },
            # Логгер для сервисов
            "app.services": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            },
            # Логгер для аутентификации
            "app.auth": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            },
            # Логгер для базы данных
            "sqlalchemy.engine": {
                "level": "WARNING",  # Только предупреждения и ошибки
                "handlers": ["console"],
                "propagate": False
            },
            # Логгер для FastAPI
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["api_requests"],
                "propagate": False
            }
        }
    }
    
    # В продакшене используем JSON формат для лучшей обработки логов
    if os.getenv("ENVIRONMENT") == "production":
        config["handlers"]["console"]["formatter"] = "json"
        config["handlers"]["file"]["formatter"] = "json"
    
    return config


def setup_logging():
    """
    Настраивает логирование для приложения.
    """
    # Создаем директорию для логов если её нет
    os.makedirs("logs", exist_ok=True)
    
    # Применяем конфигурацию
    config = get_logging_config()
    logging.config.dictConfig(config)
    
    # Получаем логгер для приложения
    logger = logging.getLogger("app")
    logger.info("Logging configured successfully")
    
    return logger


class StructuredLogger:
    """
    Структурированный логгер для лучшего мониторинга.
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_user_action(self, user_id: int, action: str, details: Dict[str, Any] = None):
        """
        Логирует действие пользователя.
        
        Args:
            user_id: ID пользователя
            action: Действие
            details: Дополнительные детали
        """
        message = f"User {user_id} performed action: {action}"
        if details:
            message += f" - Details: {details}"
        
        self.logger.info(message, extra={
            "user_id": user_id,
            "action": action,
            "details": details or {},
            "event_type": "user_action"
        })
    
    def log_api_call(self, endpoint: str, method: str, user_id: int = None, 
                     status_code: int = None, duration: float = None):
        """
        Логирует API вызов.
        
        Args:
            endpoint: Эндпоинт
            method: HTTP метод
            user_id: ID пользователя (если авторизован)
            status_code: Код ответа
            duration: Время выполнения в секундах
        """
        message = f"{method} {endpoint}"
        if status_code:
            message += f" - {status_code}"
        if duration:
            message += f" - {duration:.3f}s"
        
        self.logger.info(message, extra={
            "endpoint": endpoint,
            "method": method,
            "user_id": user_id,
            "status_code": status_code,
            "duration": duration,
            "event_type": "api_call"
        })
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """
        Логирует ошибку с контекстом.
        
        Args:
            error: Исключение
            context: Контекст ошибки
        """
        message = f"Error occurred: {str(error)}"
        if context:
            message += f" - Context: {context}"
        
        self.logger.error(message, extra={
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "event_type": "error"
        }, exc_info=True)
    
    def log_performance(self, operation: str, duration: float, 
                       details: Dict[str, Any] = None):
        """
        Логирует метрики производительности.
        
        Args:
            operation: Название операции
            duration: Время выполнения в секундах
            details: Дополнительные детали
        """
        message = f"Performance: {operation} took {duration:.3f}s"
        if details:
            message += f" - {details}"
        
        # Предупреждение для медленных операций
        log_level = logging.WARNING if duration > 1.0 else logging.INFO
        
        self.logger.log(log_level, message, extra={
            "operation": operation,
            "duration": duration,
            "details": details or {},
            "event_type": "performance"
        })


# Создаем глобальные логгеры для разных компонентов
app_logger = StructuredLogger("app")
auth_logger = StructuredLogger("app.auth")
service_logger = StructuredLogger("app.services")
api_logger = StructuredLogger("api.requests")