#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edge TTS сервис для высококачественного польского произношения
Использует Microsoft Edge TTS API для лучшего качества голосов
"""

import asyncio
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict
import tempfile
import os

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logging.warning("Edge TTS не установлен. Используйте: pip install edge-tts")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - EDGE_TTS - %(levelname)s - %(message)s')

# Директории для сохранения файлов
BASE_DIR = Path(__file__).parent.parent.parent  # backend/
AUDIO_DIR = BASE_DIR / "frontend" / "assets" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Маппинг языков на Edge TTS голоса (высокое качество)
EDGE_VOICE_MAPPING = {
    # Польский - несколько вариантов голосов
    'pl': {
        'voice': 'pl-PL-ZofiaNeural',
        'backup_voices': ['pl-PL-MarekNeural'],
        'language': 'pl-PL',
        'quality': 'Neural'
    },
    
    # Русский
    'ru': {
        'voice': 'ru-RU-SvetlanaNeural',
        'backup_voices': ['ru-RU-DmitryNeural'],
        'language': 'ru-RU',
        'quality': 'Neural'
    },
    
    # Португальский (Европейский)
    'pt': {
        'voice': 'pt-PT-RaquelNeural',
        'backup_voices': ['pt-PT-DuarteNeural'],
        'language': 'pt-PT',
        'quality': 'Neural'
    },
    
    # Португальский (Бразильский)
    'pt-BR': {
        'voice': 'pt-BR-FranciscaNeural',
        'backup_voices': ['pt-BR-AntonioNeural'],
        'language': 'pt-BR',
        'quality': 'Neural'
    },
    
    # Английский (США)
    'en': {
        'voice': 'en-US-JennyNeural',
        'backup_voices': ['en-US-GuyNeural', 'en-US-AriaNeural'],
        'language': 'en-US',
        'quality': 'Neural'
    },
    
    # Немецкий
    'de': {
        'voice': 'de-DE-KatjaNeural',
        'backup_voices': ['de-DE-ConradNeural'],
        'language': 'de-DE',
        'quality': 'Neural'
    },
    
    # Французский
    'fr': {
        'voice': 'fr-FR-DeniseNeural',
        'backup_voices': ['fr-FR-HenriNeural'],
        'language': 'fr-FR',
        'quality': 'Neural'
    },
    
    # Испанский
    'es': {
        'voice': 'es-ES-ElviraNeural',
        'backup_voices': ['es-ES-AlvaroNeural'],
        'language': 'es-ES',
        'quality': 'Neural'
    }
}

class EdgeTTSService:
    """
    Edge TTS сервис для высококачественной генерации речи
    Особенно эффективен для польского языка
    """
    
    def __init__(self):
        self.is_available = EDGE_TTS_AVAILABLE
        if not self.is_available:
            logging.warning("Edge TTS недоступен")
    
    def _generate_filename(self, text: str, language_id: str, voice: str) -> str:
        """Генерация уникального имени файла"""
        text_hash = hashlib.md5(text.encode()).hexdigest()[:12]
        voice_short = voice.split('-')[-1].replace('Neural', '')  # Например: ZofiaNeural -> Zofia
        return f"edge_{language_id}_{voice_short}_{text_hash}.mp3"
    
    def _get_voice_config(self, language_id: str) -> Dict[str, any]:
        """Получение конфигурации голоса для языка"""
        # Прямое соответствие
        if language_id in EDGE_VOICE_MAPPING:
            return EDGE_VOICE_MAPPING[language_id]
        
        # Попытка найти по базовому языку (например, pt-BR -> pt)
        base_lang = language_id.split('-')[0]
        if base_lang in EDGE_VOICE_MAPPING:
            return EDGE_VOICE_MAPPING[base_lang]
        
        # Fallback на английский
        logging.warning(f"Голос для языка '{language_id}' не найден, используем английский")
        return EDGE_VOICE_MAPPING['en']
    
    async def generate_audio(self, text: str, language_id: str, prefix: str = "edge") -> Optional[str]:
        """
        Генерация аудио с помощью Edge TTS
        
        Args:
            text: Текст для озвучки
            language_id: Код языка (например, 'pl', 'pt', 'ru')
            prefix: Префикс для имени файла
        
        Returns:
            Относительный путь к аудио файлу или None при ошибке
        """
        
        if not self.is_available:
            logging.warning("Edge TTS недоступен, пропускаем генерацию")
            return None
        
        try:
            # Получаем конфигурацию голоса
            voice_config = self._get_voice_config(language_id)
            voice_name = voice_config['voice']
            
            # Генерируем имя файла
            filename = self._generate_filename(text, language_id, voice_name)
            file_path = AUDIO_DIR / filename
            
            # Проверяем кэш
            if file_path.exists():
                logging.info(f"🎵 Edge аудио найдено в кэше: {filename}")
                return f"assets/audio/{filename}"
            
            # ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ
            logging.info(f"🔊 EDGE TTS ГЕНЕРАЦИЯ:")
            logging.info(f"   📝 Текст: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            logging.info(f"   🌍 Входной language_id: '{language_id}'")
            logging.info(f"   🎯 Edge язык: '{voice_config['language']}'")
            logging.info(f"   🎤 Edge голос: '{voice_name}'")
            logging.info(f"   🏆 Качество: '{voice_config['quality']}'")
            logging.info(f"   📁 Файл: {filename}")
            
            # Создаем коммуникатор Edge TTS
            communicate = edge_tts.Communicate(text, voice_name)
            
            # Генерируем аудио
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            if not audio_data:
                logging.error(f"❌ Edge TTS не вернул аудио данные для '{text[:30]}...'")
                return None
            
            # Сохраняем файл
            with open(file_path, 'wb') as f:
                f.write(audio_data)
            
            file_size = file_path.stat().st_size
            logging.info(f"✅ Edge аудио создано: '{text[:30]}...' ({language_id}) -> {filename} ({file_size} байт)")
            return f"assets/audio/{filename}"
            
        except Exception as e:
            logging.error(f"❌ Исключение в Edge TTS: {e}")
            
            # Попробуем backup голос
            voice_config = self._get_voice_config(language_id)
            if 'backup_voices' in voice_config and voice_config['backup_voices']:
                for backup_voice in voice_config['backup_voices']:
                    try:
                        logging.info(f"🔄 Пробуем backup голос: {backup_voice}")
                        
                        communicate = edge_tts.Communicate(text, backup_voice)
                        audio_data = b""
                        async for chunk in communicate.stream():
                            if chunk["type"] == "audio":
                                audio_data += chunk["data"]
                        
                        if audio_data:
                            filename = self._generate_filename(text, language_id, backup_voice)
                            file_path = AUDIO_DIR / filename
                            
                            with open(file_path, 'wb') as f:
                                f.write(audio_data)
                            
                            logging.info(f"✅ Edge backup аудио создано: {backup_voice}")
                            return f"assets/audio/{filename}"
                            
                    except Exception as backup_e:
                        logging.warning(f"⚠️ Backup голос {backup_voice} тоже не сработал: {backup_e}")
                        continue
            
            return None
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Получение списка поддерживаемых языков"""
        return {
            lang_code: config['voice']
            for lang_code, config in EDGE_VOICE_MAPPING.items()
        }
    
    def is_language_supported(self, language_id: str) -> bool:
        """Проверка поддержки языка"""
        return language_id in EDGE_VOICE_MAPPING or language_id.split('-')[0] in EDGE_VOICE_MAPPING
    
    def get_service_info(self) -> Dict[str, any]:
        """Информация о сервисе"""
        return {
            'service': 'Microsoft Edge TTS',
            'available': self.is_available,
            'supported_languages': len(EDGE_VOICE_MAPPING),
            'voice_quality': 'Neural (Premium Quality)',
            'polish_support': 'Excellent',
            'cost': 'Free'
        }

# Создаем глобальный экземпляр сервиса
edge_tts_service = EdgeTTSService()

# Функция для совместимости
async def generate_audio_edge(text: str, language_id: str, prefix: str = "edge") -> Optional[str]:
    """Функция-обертка для генерации аудио через Edge TTS"""
    return await edge_tts_service.generate_audio(text, language_id, prefix)