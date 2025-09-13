#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS Service (заглушка)
Временный файл для совместимости с tts.py роутером
"""

import logging
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - TTS_SERVICE - %(levelname)s - %(message)s')

class TTSService:
    """
    Заглушка для TTS сервиса
    """
    
    def __init__(self):
        self._available = False
        logging.info("TTS сервис инициализирован (заглушка)")
    
    def is_available(self) -> bool:
        """Проверка доступности сервиса"""
        return self._available
    
    async def generate_audio(self, text: str, language_id: str, prefix: str = "tts") -> Optional[str]:
        """Генерация аудио (заглушка)"""
        logging.warning(f"TTS сервис недоступен для '{text[:30]}...' ({language_id})")
        return None
    
    def get_service_info(self) -> dict:
        """Информация о сервисе"""
        return {
            'service': 'TTS Service',
            'available': False,
            'status': 'Not implemented (stub)'
        }
    
    def get_supported_languages(self) -> list:
        """Получение списка поддерживаемых языков"""
        return []
    
    def get_voices_for_language(self, language_code: str) -> list:
        """Получение голосов для языка"""
        return []

# Создаем глобальный экземпляр сервиса
tts_service = TTSService()

# Функции для совместимости
async def generate_tts_audio(text: str, language_id: str, voice_id: str = None) -> Optional[str]:
    """Функция-обертка для генерации TTS аудио"""
    return await tts_service.generate_audio(text, language_id, "tts")

def get_available_voices(language_code: str = None) -> list:
    """Получение доступных голосов"""
    if language_code:
        return tts_service.get_voices_for_language(language_code)
    return tts_service.get_supported_languages()