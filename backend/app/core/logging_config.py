import logging
import logging.config
import os
from pathlib import Path

# Создаем директорию для логов
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Конфигурация логирования
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': str(LOGS_DIR / 'app.log'),
            'mode': 'a',
            'encoding': 'utf-8'
        },
        'ai_file': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'formatter': 'detailed',
            'filename': str(LOGS_DIR / 'ai_service.log'),
            'mode': 'a',
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        'backend.app.services.ai_service': {
            'level': 'INFO',
            'handlers': ['console', 'ai_file'],
            'propagate': False
        },
        'uvicorn': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'uvicorn.access': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': False
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}

def setup_logging():
    """Настройка логирования для приложения"""
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Создаем логгер для проверки
    logger = logging.getLogger(__name__)
    logger.info("Логирование настроено успешно")
    logger.info(f"Логи сохраняются в: {LOGS_DIR}")