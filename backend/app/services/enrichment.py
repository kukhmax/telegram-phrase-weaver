# Файл: core/enrichment.py (ОБНОВЛЕННАЯ ВЕРСИЯ v7)

import asyncio, logging, os, hashlib, aiohttp
from pathlib import Path
from typing import Optional
from core.ai_generator import generate_examples_with_ai
from core.image_finder import find_image_via_api
from gtts import gTTS
from googletrans import Translator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - ENRICH - %(levelname)s - %(message)s')
AUDIO_DIR, IMAGE_DIR = Path("assets/audio"), Path("assets/images")

def ensure_dir_exists(*dirs): [d.mkdir(parents=True, exist_ok=True) for d in dirs if not d.exists()]
ensure_dir_exists(AUDIO_DIR, IMAGE_DIR)

async def get_translation(text: str, from_lang: str, to_lang: str) -> Optional[str]:
    try:
        def translate_sync(): return Translator().translate(text, src=from_lang, dest=to_lang).text
        return await asyncio.get_running_loop().run_in_executor(None, translate_sync)
    except Exception as e: logging.error(f"Ошибка перевода: {e}"); return None

async def generate_audio(text: str, lang: str, prefix: str):
    try:
        path = AUDIO_DIR / f"{prefix}_{hashlib.md5(text.encode()).hexdigest()[:8]}.mp3"
        if path.exists(): return str(path)
        
        tld_map = {'pt': 'pt'}
        tld = tld_map.get(lang, 'com')

        tts = await asyncio.get_running_loop().run_in_executor(None, lambda: gTTS(text=text, lang=lang, tld=tld, slow=False))
        await asyncio.get_running_loop().run_in_executor(None, tts.save, str(path))
        logging.info(f"Аудио '{text}' ({lang} / {tld}) сохранено: {path}")
        return str(path)
    except Exception as e:
        logging.error(f"Ошибка генерации аудио: {e}"); return None

async def download_and_save_image(image_url: str, query: str) -> Optional[str]:
    if not image_url: return None
    try:
        path = IMAGE_DIR / f"{hashlib.md5(query.encode()).hexdigest()}{Path(image_url.split('?')[0]).suffix or '.jpg'}"
        async with aiohttp.ClientSession() as s, s.get(image_url) as r:
            if r.status == 200:
                with open(path, 'wb') as f: f.write(await r.read())
                return str(path)
    except Exception as e: logging.error(f"Ошибка скачивания картинки: {e}"); return None

async def enrich_phrase(phrase: str, keyword: str, lang_code: str, target_lang: str) -> Optional[dict]:
    """
    Обогащает фразу, используя исходную фразу и ключевое слово.
    
    Args:
        phrase: Исходная фраза для изучения
        keyword: Ключевое слово в фразе
        lang_code: Код языка изучения
        target_lang: Код языка перевода
    """
    logging.info(f"--- НАЧАЛО ОБОГАЩЕНИЯ (v7) для фразы '{phrase}' с ключевым словом '{keyword}' на '{target_lang}' ---")
    
    lang_map = {'en': 'English', 'ru': 'Russian', 'es': 'Spanish', 'pt': 'Portuguese', 'pl': 'Polish'}
    target_lang_full = lang_map.get(target_lang, target_lang)
    language_full = lang_map.get(lang_code, lang_code)
    
    # Вызываем AI с новой сигнатурой функции
    ai_data = await generate_examples_with_ai(phrase, keyword, language_full, target_lang_full)
    if not ai_data: 
        logging.error("Не удалось получить данные от AI")
        return None

    # Извлекаем данные из нового формата JSON
    image_query = ai_data.get("image_query", keyword)
    original_phrase_data = ai_data.get("original_phrase", {})
    additional_examples = ai_data.get("additional_examples", [])
    
    # Переводим запрос для поиска картинки на английский, если нужно
    english_image_query = image_query
    if lang_code != 'en':
        translated_query = await get_translation(image_query, from_lang=lang_code, to_lang='en')
        if translated_query: 
            english_image_query = translated_query
        
    # Находим картинку
    image_url_from_api = await find_image_via_api(english_image_query)

    # Параллельные задачи
    tasks = [
        get_translation(keyword, from_lang=lang_code, to_lang=target_lang),  # перевод ключевого слова
        download_and_save_image(image_url_from_api, english_image_query),    # скачивание картинки
        generate_audio(keyword, lang_code, "keyword"),                       # аудио ключевого слова
        generate_audio(phrase, lang_code, "phrase")                          # аудио исходной фразы
    ]

    gathered_results = await asyncio.gather(*tasks)
    
    keyword_translation = gathered_results[0]
    image_path = gathered_results[1]
    keyword_audio_path = gathered_results[2]
    phrase_audio_path = gathered_results[3]
    
    # Формируем результат в новом формате
    result = {
        'keyword': keyword,
        'keyword_translation': keyword_translation,
        'keyword_audio_path': keyword_audio_path,
        'phrase': phrase,
        'phrase_audio_path': phrase_audio_path,
        'original_phrase': original_phrase_data,  # содержит original и translation
        'additional_examples': additional_examples,  # список из 5 примеров
        'image_path': image_path
    }
    
    logging.info(f"--- ОБОГАЩЕНИЕ ЗАВЕРШЕНО для '{phrase}' ---")
    return result