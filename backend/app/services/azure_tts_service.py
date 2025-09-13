#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Azure TTS сервис (заглушка)
В данный момент не используется, но импортируется в enrichment.py
"""

import logging
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - AZURE_TTS - %(levelname)s - %(message)s')

class AzureTTSService:
    """
    Заглушка для Azure TTS сервиса
    """
    
    def __init__(self):
        self._available = False
        logging.info("Azure TTS сервис инициализирован (заглушка)")
    
    def is_available(self) -> bool:
        """Проверка доступности сервиса"""
        return self._available
    
    async def generate_audio(self, text: str, language_id: str, prefix: str = "azure") -> Optional[str]:
        """Генерация аудио (заглушка)"""
        logging.warning(f"Azure TTS недоступен для '{text[:30]}...' ({language_id})")
        return None
    
    def get_service_info(self) -> dict:
        """Информация о сервисе"""
        return {
            'service': 'Azure TTS',
            'available': False,
            'status': 'Not implemented (stub)'
        }

# Создаем глобальный экземпляр сервиса
azure_tts_service = AzureTTSService()