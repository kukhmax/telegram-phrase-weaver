# backend/app/services/tts_service.py

import asyncio
import hashlib
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any
# Временно отключаем torch импорты
# import torch
# import torchaudio as ta
from functools import lru_cache

# Временно отключаем Chatterbox TTS из-за проблем совместимости с Python 3.11
# TODO: Исправить установку chatterbox-tts
CHATTERBOX_AVAILABLE = False
logging.warning("Chatterbox TTS временно отключен. Используется gTTS.")

from gtts import gTTS
from ..core.config import get_settings

settings = get_settings()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - TTS - %(levelname)s - %(message)s')

# Директории для аудиофайлов
BASE_DIR = Path(__file__).parent.parent.parent  # backend/
AUDIO_DIR = BASE_DIR / "frontend" / "assets" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Поддерживаемые языки Chatterbox
CHATTERBOX_LANGUAGES = {
    'ar': 'ar',  # Arabic
    'da': 'da',  # Danish
    'de': 'de',  # German
    'el': 'el',  # Greek
    'en': 'en',  # English
    'es': 'es',  # Spanish
    'fi': 'fi',  # Finnish
    'fr': 'fr',  # French
    'he': 'he',  # Hebrew
    'hi': 'hi',  # Hindi
    'it': 'it',  # Italian
    'ja': 'ja',  # Japanese
    'ko': 'ko',  # Korean
    'ms': 'ms',  # Malay
    'nl': 'nl',  # Dutch
    'no': 'no',  # Norwegian
    'pl': 'pl',  # Polish
    'pt': 'pt',  # Portuguese
    'ru': 'ru',  # Russian
    'sv': 'sv',  # Swedish
    'sw': 'sw',  # Swahili
    'tr': 'tr',  # Turkish
    'zh': 'zh'   # Chinese
}

class TTSService:
    """Сервис для генерации речи с поддержкой Chatterbox TTS и fallback на gTTS"""
    
    def __init__(self):
        # Временно отключаем CUDA проверку
        self.device = "cpu"  # torch.cuda.is_available() if torch else "cpu"
        self.english_model = None
        self.multilingual_model = None
        self._model_loading_lock = asyncio.Lock()
        
        logging.info(f"TTS Service инициализирован. Device: {self.device}, Chatterbox доступен: {CHATTERBOX_AVAILABLE}")
    
    @lru_cache(maxsize=1)
    def _get_english_model(self):
        """Ленивая загрузка английской модели"""
        if not CHATTERBOX_AVAILABLE:
            return None
        try:
            model = ChatterboxTTS.from_pretrained(device=self.device)
            logging.info("Английская модель Chatterbox загружена")
            return model
        except Exception as e:
            logging.error(f"Ошибка загрузки английской модели: {e}")
            return None
    
    @lru_cache(maxsize=1)
    def _get_multilingual_model(self):
        """Ленивая загрузка многоязычной модели"""
        if not CHATTERBOX_AVAILABLE:
            return None
        try:
            model = ChatterboxMultilingualTTS.from_pretrained(device=self.device)
            logging.info("Многоязычная модель Chatterbox загружена")
            return model
        except Exception as e:
            logging.error(f"Ошибка загрузки многоязычной модели: {e}")
            return None
    
    async def _load_models_if_needed(self, language_id: str):
        """Асинхронная загрузка моделей при необходимости"""
        async with self._model_loading_lock:
            if language_id == 'en' and self.english_model is None:
                self.english_model = await asyncio.get_running_loop().run_in_executor(
                    None, self._get_english_model
                )
            elif language_id != 'en' and self.multilingual_model is None:
                self.multilingual_model = await asyncio.get_running_loop().run_in_executor(
                    None, self._get_multilingual_model
                )
    
    def _generate_filename(self, text: str, language_id: str, prefix: str = "tts") -> str:
        """Генерирует уникальное имя файла на основе текста и языка"""
        text_hash = hashlib.md5(f"{text}_{language_id}".encode()).hexdigest()[:12]
        return f"{prefix}_{language_id}_{text_hash}.wav"
    
    async def _generate_with_chatterbox(self, text: str, language_id: str, 
                                      audio_prompt_path: Optional[str] = None,
                                      exaggeration: float = 0.5,
                                      cfg_weight: float = 0.5) -> Optional[str]:
        """Генерация аудио с помощью Chatterbox TTS"""
        try:
            await self._load_models_if_needed(language_id)
            
            if language_id == 'en' and self.english_model:
                model = self.english_model
                wav = await asyncio.get_running_loop().run_in_executor(
                    None, 
                    lambda: model.generate(
                        text, 
                        audio_prompt_path=audio_prompt_path,
                        exaggeration=exaggeration,
                        cfg_weight=cfg_weight
                    )
                )
            elif self.multilingual_model:
                model = self.multilingual_model
                wav = await asyncio.get_running_loop().run_in_executor(
                    None,
                    lambda: model.generate(
                        text,
                        language_id=language_id,
                        audio_prompt_path=audio_prompt_path,
                        exaggeration=exaggeration,
                        cfg_weight=cfg_weight
                    )
                )
            else:
                return None
            
            filename = self._generate_filename(text, language_id, "chatterbox")
            file_path = AUDIO_DIR / filename
            
            # Сохраняем аудио (временно отключено)
            # await asyncio.get_running_loop().run_in_executor(
            #     None, 
            #     lambda: ta.save(str(file_path), wav, model.sr)
            # )
            # Временная заглушка
            return None
            
            logging.info(f"Chatterbox TTS: '{text[:50]}...' ({language_id}) -> {filename}")
            return f"assets/audio/{filename}"
            
        except Exception as e:
            logging.error(f"Ошибка Chatterbox TTS: {e}")
            return None
    
    async def _generate_with_gtts(self, text: str, language_id: str) -> Optional[str]:
        """Fallback генерация с помощью gTTS"""
        try:
            filename = self._generate_filename(text, language_id, "gtts")
            file_path = AUDIO_DIR / filename
            
            # Маппинг языков для gTTS
            gtts_lang_map = {
                'pt': 'pt', 'en': 'en', 'es': 'es', 'fr': 'fr', 
                'de': 'de', 'it': 'it', 'ru': 'ru', 'ja': 'ja',
                'ko': 'ko', 'zh': 'zh', 'ar': 'ar', 'hi': 'hi'
            }
            
            gtts_lang = gtts_lang_map.get(language_id, 'en')
            tld_map = {'pt': 'pt'}
            tld = tld_map.get(gtts_lang, 'com')
            
            def tts_sync():
                tts = gTTS(text=text, lang=gtts_lang, tld=tld, slow=False)
                tts.save(str(file_path))
            
            await asyncio.get_running_loop().run_in_executor(None, tts_sync)
            
            logging.info(f"gTTS fallback: '{text[:50]}...' ({language_id}) -> {filename}")
            return f"assets/audio/{filename}"
            
        except Exception as e:
            logging.error(f"Ошибка gTTS: {e}")
            return None
    
    async def generate_audio(self, text: str, language_id: str, 
                           use_chatterbox: bool = True,
                           audio_prompt_path: Optional[str] = None,
                           exaggeration: float = 0.5,
                           cfg_weight: float = 0.5,
                           prefix: str = "tts") -> Optional[str]:
        """
        Генерирует аудиофайл для заданного текста
        
        Args:
            text: Текст для озвучки
            language_id: Код языка (ISO 639-1)
            use_chatterbox: Использовать Chatterbox TTS (если доступен)
            audio_prompt_path: Путь к аудио-промпту для клонирования голоса
            exaggeration: Уровень выразительности (0.0-1.0)
            cfg_weight: Вес конфигурации (0.0-1.0)
            prefix: Префикс для имени файла
            
        Returns:
            Относительный путь к сгенерированному аудиофайлу или None
        """
        if not text or not text.strip():
            return None
        
        text = text.strip()
        
        # Проверяем кэш
        filename = self._generate_filename(text, language_id, 
                                         "chatterbox" if use_chatterbox else "gtts")
        file_path = AUDIO_DIR / filename
        
        if file_path.exists():
            logging.info(f"Аудио из кэша: {filename}")
            return f"assets/audio/{filename}"
        
        # Пытаемся использовать Chatterbox, если доступен и запрошен
        if (use_chatterbox and CHATTERBOX_AVAILABLE and 
            language_id in CHATTERBOX_LANGUAGES):
            
            result = await self._generate_with_chatterbox(
                text, language_id, audio_prompt_path, exaggeration, cfg_weight
            )
            if result:
                return result
            
            logging.warning(f"Chatterbox не смог обработать '{text}', используем gTTS")
        
        # Fallback на gTTS
        return await self._generate_with_gtts(text, language_id)
    
    async def generate_batch_audio(self, texts_and_langs: list[tuple[str, str]], 
                                 **kwargs) -> Dict[str, Optional[str]]:
        """
        Генерирует аудио для нескольких текстов параллельно
        
        Args:
            texts_and_langs: Список кортежей (text, language_id)
            **kwargs: Дополнительные параметры для generate_audio
            
        Returns:
            Словарь {text: audio_path}
        """
        tasks = [
            self.generate_audio(text, lang, **kwargs) 
            for text, lang in texts_and_langs
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            text: result if not isinstance(result, Exception) else None
            for (text, _), result in zip(texts_and_langs, results)
        }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Возвращает список поддерживаемых языков"""
        if CHATTERBOX_AVAILABLE:
            return CHATTERBOX_LANGUAGES
        else:
            # Базовые языки для gTTS
            return {
                'en': 'en', 'es': 'es', 'fr': 'fr', 'de': 'de',
                'it': 'it', 'pt': 'pt', 'ru': 'ru', 'ja': 'ja',
                'ko': 'ko', 'zh': 'zh', 'ar': 'ar', 'hi': 'hi'
            }
    
    def cleanup_old_files(self, max_age_days: int = 7):
        """Очищает старые аудиофайлы"""
        import time
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        deleted_count = 0
        for file_path in AUDIO_DIR.glob("*.wav"):
            if current_time - file_path.stat().st_mtime > max_age_seconds:
                file_path.unlink()
                deleted_count += 1
        
        if deleted_count > 0:
            logging.info(f"Удалено {deleted_count} старых аудиофайлов")


# Глобальный экземпляр сервиса
tts_service = TTSService()


# Функции для обратной совместимости
async def generate_audio_chatterbox(text: str, language_id: str, 
                                  audio_prompt_path: Optional[str] = None,
                                  exaggeration: float = 0.5,
                                  cfg_weight: float = 0.5) -> Optional[str]:
    """Генерация аудио с помощью Chatterbox TTS"""
    return await tts_service.generate_audio(
        text, language_id, use_chatterbox=True,
        audio_prompt_path=audio_prompt_path,
        exaggeration=exaggeration, cfg_weight=cfg_weight
    )


async def generate_audio_gtts(text: str, language_id: str) -> Optional[str]:
    """Генерация аудио с помощью gTTS (fallback)"""
    return await tts_service.generate_audio(text, language_id, use_chatterbox=False)