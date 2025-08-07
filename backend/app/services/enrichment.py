# Файл: core/enrichment.py (ФИНАЛЬНАЯ ВЕРСИЯ v6)

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

# --- ИЗМЕНЕНИЕ ЗДЕСЬ: Убираем ненужный параметр 'target_lang' ---
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

async def enrich_phrase(keyword: str, full_sentence: str, lang_code: str, target_lang: str) -> Optional[dict]:
    logging.info(f"--- НАЧАЛО ОБОГАЩЕНИЯ (v6) для '{keyword}' на '{target_lang}' ---")
    lang_map = {'en': 'English', 'ru': 'Russian', 'es': 'Spanish', 'pt': 'Portuguese', 'pl': 'Polish'}
    target_lang_full = lang_map.get(target_lang, target_lang)
    
    ai_data = await generate_examples_with_ai(keyword, lang_map.get(lang_code, lang_code), target_lang_full)
    if not ai_data: return None

    image_query, examples = ai_data.get("image_query", keyword), ai_data.get("examples", [])
    
    english_image_query = image_query
    if lang_code != 'en':
        translated_query = await get_translation(image_query, from_lang=lang_code, to_lang='en')
        if translated_query: english_image_query = translated_query
        
    image_url_from_api = await find_image_via_api(english_image_query)

    tasks = [
        get_translation(keyword, from_lang=lang_code, to_lang=target_lang),
        download_and_save_image(image_url_from_api, english_image_query),
        generate_audio(keyword, lang_code, "keyword") # <-- Вызов теперь снова правильный
    ]
    if full_sentence and full_sentence != keyword:
        tasks.append(get_translation(full_sentence, from_lang=lang_code, to_lang=target_lang))

    gathered_results = await asyncio.gather(*tasks)
    
    keyword_translation, image_path, keyword_audio_path = gathered_results[0], gathered_results[1], gathered_results[2]
    full_sentence_translation = gathered_results[3] if (full_sentence and full_sentence != keyword) else None
    
    return {'keyword': keyword, 'translation': keyword_translation,
            'full_sentence_translation': full_sentence_translation, 'examples': examples,
            'image_path': image_path, 'audio_path': keyword_audio_path}