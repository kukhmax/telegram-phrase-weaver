import asyncio
import logging
import os
import hashlib
from pathlib import Path
from typing import Optional
import aiohttp
from gtts import gTTS
from .tts_service import tts_service
from deep_translator import GoogleTranslator

from .ai_service import generate_examples_with_ai  # Импорт AI
from .image_finder import find_image_via_api  # Импорт image

logging.basicConfig(level=logging.INFO, format='%(asctime)s - ENRICH - %(levelname)s - %(message)s')

# Получаем абсолютные пути к директориям
BASE_DIR = Path(__file__).parent.parent.parent  # backend/
AUDIO_DIR = BASE_DIR / "frontend" / "assets" / "audio"
IMAGE_DIR = BASE_DIR / "frontend" / "assets" / "images"

def ensure_dir_exists(*dirs): [d.mkdir(parents=True, exist_ok=True) for d in dirs if not d.exists()]
ensure_dir_exists(AUDIO_DIR, IMAGE_DIR)

async def get_translation(text: str, from_lang: str, to_lang: str) -> Optional[str]:
    try:
        def translate_sync():
            return GoogleTranslator(source=from_lang, target=to_lang).translate(text)
        return await asyncio.get_running_loop().run_in_executor(None, translate_sync)
    except Exception as e: 
        logging.error(f"Ошибка перевода: {e}")
        return None

async def generate_audio(text: str, lang: str, prefix: str, use_chatterbox: bool = True):
    """
    Генерирует аудио с использованием нового TTS сервиса
    
    Args:
        text: Текст для озвучки
        lang: Код языка
        prefix: Префикс для имени файла
        use_chatterbox: Использовать Chatterbox TTS (по умолчанию True)
    """
    try:
        # Используем новый TTS сервис
        audio_path = await tts_service.generate_audio(
            text=text,
            language_id=lang,
            use_chatterbox=use_chatterbox,
            prefix=prefix
        )
        
        if audio_path:
            logging.info(f"Аудио '{text}' ({lang}) сохранено через TTS сервис: {audio_path}")
            return audio_path
        else:
            logging.warning(f"TTS сервис не смог сгенерировать аудио для '{text}' ({lang})")
            return None
            
    except Exception as e:
        logging.error(f"Ошибка генерации аудио через TTS сервис: {e}")
        # Fallback на старый метод
        return await generate_audio_legacy(text, lang, prefix)


async def generate_audio_legacy(text: str, lang: str, prefix: str):
    """
    Старый метод генерации аудио с gTTS (fallback)
    """
    try:
        filename = f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:8]}.mp3"
        file_path = AUDIO_DIR / filename
        
        # Если файл уже существует, возвращаем относительный путь
        if file_path.exists(): 
            return f"assets/audio/{filename}"
        
        tld_map = {'pt': 'pt'}
        tld = tld_map.get(lang, 'com')

        def tts_sync():
            tts = gTTS(text=text, lang=lang, tld=tld, slow=False)
            tts.save(str(file_path))
        
        await asyncio.get_running_loop().run_in_executor(None, tts_sync)
        logging.info(f"Аудио '{text}' ({lang} / {tld}) сохранено (legacy): {file_path}")
        return f"assets/audio/{filename}"
    except Exception as e:
        logging.error(f"Ошибка генерации аудио (legacy): {e}")
        return None

async def download_and_save_image(image_url: str, query: str) -> Optional[str]:
    if not image_url: return None
    try:
        filename = f"{hashlib.md5(query.encode()).hexdigest()}{Path(image_url.split('?')[0]).suffix or '.jpg'}"
        file_path = IMAGE_DIR / filename
        
        # Если файл уже существует, возвращаем относительный путь
        if file_path.exists():
            return f"assets/images/{filename}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(file_path, 'wb') as f: 
                        f.write(content)
                    logging.info(f"Изображение для '{query}' сохранено: {file_path}")
                    return f"assets/images/{filename}"
    except Exception as e: 
        logging.error(f"Ошибка скачивания картинки: {e}")
        return None

async def enrich_phrase(phrase: str, keyword: str, lang_code: str, target_lang: str) -> Optional[dict]:
    """
    Обогащает фразу (как в оригинале), с вызовами AI и image (async).
    """
    logging.info(f"--- НАЧАЛО ОБОГАЩЕНИЯ для фразы '{phrase}' с ключевым словом '{keyword}' на '{target_lang}' ---")
    
    lang_map = {
        'en': 'English', 
        'ru': 'Russian', 
        'es': 'Spanish', 
        'pt': 'Portuguese', 
        'pl': 'Polish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian'
    }
    target_lang_full = lang_map.get(target_lang, target_lang)
    language_full = lang_map.get(lang_code, lang_code)
    
    # Вызов AI (async, с cache)
    ai_data = await generate_examples_with_ai(phrase, keyword, language_full, target_lang_full)
    if not ai_data: 
        logging.error("Не удалось получить данные от AI")
        return {"error": "AI сервис недоступен"}
    
    # Проверяем, есть ли ошибка в ответе AI
    if isinstance(ai_data, dict) and "error" in ai_data:
        logging.error(f"Ошибка от AI сервиса: {ai_data['error']}")
        return ai_data  # Возвращаем ошибку как есть

    image_query = ai_data.get("image_query", keyword)
    original_phrase_data = ai_data.get("original_phrase", {})
    additional_examples = ai_data.get("additional_examples", [])
    
    # Перевод image_query если нужно (async)
    english_image_query = image_query
    if lang_code != 'en':
        translated_query = await get_translation(image_query, from_lang=lang_code, to_lang='en')
        if translated_query: 
            english_image_query = translated_query
    
    # Находим image (async)
    image_url_from_api = await find_image_via_api(english_image_query)

    # Параллельные задачи (gather для async)
    tasks = [
        get_translation(keyword, from_lang=lang_code, to_lang=target_lang),  # перевод keyword
        download_and_save_image(image_url_from_api, english_image_query),    # download image
        generate_audio(keyword, lang_code, "keyword"),                       # audio keyword
        generate_audio(phrase, lang_code, "phrase")                          # audio phrase
    ]

    gathered_results = await asyncio.gather(*tasks)
    
    keyword_translation = gathered_results[0]
    image_path = gathered_results[1]
    keyword_audio_path = gathered_results[2]
    phrase_audio_path = gathered_results[3]
    
    # Результат (как в оригинале)
    result = {
        'keyword': keyword,
        'keyword_translation': keyword_translation,
        'keyword_audio_path': keyword_audio_path,
        'phrase': phrase,
        'phrase_audio_path': phrase_audio_path,
        'original_phrase': original_phrase_data,
        'additional_examples': additional_examples,
        'image_path': image_path
    }
    
    logging.info(f"--- ОБОГАЩЕНИЕ ЗАВЕРШЕНО для '{phrase}' ---")
    return result