import asyncio
import logging
import os
import hashlib
from pathlib import Path
from typing import Optional
import aiohttp
from gtts import gTTS
from deep_translator import GoogleTranslator

from .ai_service import generate_examples_with_ai  # Импорт AI
from .image_finder import find_image_via_api  # Импорт image

logging.basicConfig(level=logging.INFO, format='%(asctime)s - ENRICH - %(levelname)s - %(message)s')
AUDIO_DIR, IMAGE_DIR = Path("frontend/assets/audio"), Path("frontend/assets/images")

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

async def generate_audio(text: str, lang: str, prefix: str):
    try:
        path = AUDIO_DIR / f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:8]}.mp3"
        if path.exists(): return str(path)
        
        tld_map = {'pt': 'pt'}
        tld = tld_map.get(lang, 'com')

        def tts_sync():
            tts = gTTS(text=text, lang=lang, tld=tld, slow=False)
            tts.save(str(path))
        
        await asyncio.get_running_loop().run_in_executor(None, tts_sync)
        logging.info(f"Аудио '{text}' ({lang} / {tld}) сохранено: {path}")
        return str(path)
    except Exception as e:
        logging.error(f"Ошибка генерации аудио: {e}")
        return None

async def download_and_save_image(image_url: str, query: str) -> Optional[str]:
    if not image_url: return None
    try:
        path = IMAGE_DIR / f"{hashlib.md5(query.encode()).hexdigest()}{Path(image_url.split('?')[0]).suffix or '.jpg'}"
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(path, 'wb') as f: 
                        f.write(content)
                    return str(path)
    except Exception as e: 
        logging.error(f"Ошибка скачивания картинки: {e}")
        return None

async def enrich_phrase(phrase: str, keyword: str, lang_code: str, target_lang: str) -> Optional[dict]:
    """
    Обогащает фразу (как в оригинале), с вызовами AI и image (async).
    """
    logging.info(f"--- НАЧАЛО ОБОГАЩЕНИЯ для фразы '{phrase}' с ключевым словом '{keyword}' на '{target_lang}' ---")
    
    lang_map = {'en': 'English', 'ru': 'Russian', 'es': 'Spanish', 'pt': 'Portuguese', 'pl': 'Polish'}
    target_lang_full = lang_map.get(target_lang, target_lang)
    language_full = lang_map.get(lang_code, lang_code)
    
    # Вызов AI (async, с cache)
    ai_data = await generate_examples_with_ai(phrase, keyword, language_full, target_lang_full)
    if not ai_data: 
        logging.error("Не удалось получить данные от AI")
        return None

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