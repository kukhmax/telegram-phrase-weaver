# backend/app/services/tts_service.py

import asyncio
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict

from gtts import gTTS
from ..core.config import get_settings

settings = get_settings()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - TTS - %(levelname)s - %(message)s')

# Директории для аудиофайлов
BASE_DIR = Path(__file__).parent.parent.parent  # backend/
AUDIO_DIR = BASE_DIR / "frontend" / "assets" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Поддерживаемые языки gTTS
GTTS_LANGUAGES = {
    'de': 'de',  # German
    'en': 'en',  # English
    'es': 'es',  # Spanish
    'fr': 'fr',  # French
    'hi': 'hi',  # Hindi

    'pl': 'pl',  # Polish
    'pt': 'pt',  # Portuguese
    'ru': 'ru',  # Russian
    'zh': 'zh'   # Chinese
}

class TTSService:
    """Сервис для генерации речи с использованием gTTS"""
    
    def __init__(self):
        logging.info("TTS Service инициализирован с gTTS")
    
    def _generate_filename(self, text: str, language_id: str, prefix: str = "tts") -> str:
        """Генерирует уникальное имя файла на основе текста и языка"""
        text_hash = hashlib.md5(f"{text}_{language_id}".encode()).hexdigest()[:12]
        return f"{prefix}_{language_id}_{text_hash}.wav"
    

    
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
                           prefix: str = "tts") -> Optional[str]:
        """
        Генерирует аудиофайл для заданного текста с использованием gTTS
        
        Args:
            text: Текст для озвучки
            language_id: Код языка (ISO 639-1)
            prefix: Префикс для имени файла
            
        Returns:
            Относительный путь к сгенерированному аудиофайлу или None
        """
        if not text or not text.strip():
            return None
        
        text = text.strip()
        
        # Проверяем кэш
        filename = self._generate_filename(text, language_id, "gtts")
        file_path = AUDIO_DIR / filename
        
        if file_path.exists():
            logging.info(f"Аудио из кэша: {filename}")
            return f"assets/audio/{filename}"
        
        # Генерируем с помощью gTTS
        return await self._generate_with_gtts(text, language_id)
    
    async def generate_batch_audio(self, texts_and_langs: list[tuple[str, str]], 
                                 prefix: str = "tts") -> Dict[str, Optional[str]]:
        """
        Генерирует аудио для нескольких текстов параллельно
        
        Args:
            texts_and_langs: Список кортежей (text, language_id)
            prefix: Префикс для имени файла
            
        Returns:
            Словарь {text: audio_path}
        """
        tasks = [
            self.generate_audio(text, lang, prefix=prefix) 
            for text, lang in texts_and_langs
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            text: result if not isinstance(result, Exception) else None
            for (text, _), result in zip(texts_and_langs, results)
        }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Возвращает список поддерживаемых языков gTTS"""
        return GTTS_LANGUAGES
    
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


# Функция для обратной совместимости
async def generate_audio_gtts(text: str, language_id: str) -> Optional[str]:
    """Генерация аудио с помощью gTTS"""
    return await tts_service.generate_audio(text, language_id)