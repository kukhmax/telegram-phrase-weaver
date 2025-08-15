import os
import hashlib
import json
import logging
from typing import Optional
import google.generativeai as genai

from .utils import redis_client

# Обновленный промпт с поддержкой исходной фразы
PROMPT_TEMPLATE = """
Your task is to help with language learning.
Given:
- Original phrase: "{phrase}" 
- Keyword to focus on: "{keyword}"
- Language: "{language}"
- Target language for translation: "{target_language}"

Please:
1. Create an English search query (1-2 words) for finding an image that best visually represents the keyword "{keyword}". Call this field "image_query".
2. Take the original phrase "{phrase}" and provide its accurate translation to {target_language}. In the original phrase, wrap the keyword "{keyword}" (in any of its forms) with HTML tags <b> and </b>.
3. Generate 5 additional realistic example sentences using the keyword "{keyword}" in different grammatical forms (conjugations, declensions, etc.).
4. For each of the 5 additional examples, provide accurate translations to {target_language}.
5. In each of the 5 additional examples, find and wrap the keyword "{keyword}" (in any of its forms) with HTML tags <b> and </b>.

Return ONLY a valid JSON object without any other words or formatting.
Format example:
{{
  "image_query": "walking home sunset",
  "original_phrase": {{"original": "Eu estou <b>indo</b> para casa.", "translation": "Я иду домой."}},
  "additional_examples": [
    {{"original": "Eles <b>vão</b> para a praia.", "translation": "Они идут на пляж."}},
    {{"original": "Nós <b>fomos</b> ao cinema.", "translation": "Мы пошли в кино."}},
    {{"original": "Ela <b>vai</b> trabalhar.", "translation": "Она идет работать."}},
    {{"original": "Vocês <b>foram</b> embora.", "translation": "Вы ушли."}},
    {{"original": "Eu <b>irei</b> amanhã.", "translation": "Я пойду завтра."}}
  ]
}}
"""

async def generate_examples_with_ai(phrase: str, keyword: str, language: str, target_language: str) -> Optional[dict]:
    """
    Генерирует примеры фраз с помощью AI, включая исходную фразу и дополнительные примеры.
    """
    
   # Ключ кэша: hash от phrase + keyword для uniqueness
    cache_key = f"ai:{hashlib.md5((phrase + keyword).encode()).hexdigest()}"
    
    # Проверяем кэш (async get)
    cached = await redis_client.get(cache_key)
    if cached:
        logging.info(f"AI data loaded from cache for '{phrase}'")
        return json.loads(cached)
    
    # Если нет кэша — настройка модели (как в оригинале)

    try:
        api_key = os.environ["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except KeyError:
        logging.error("КРИТИЧЕСКАЯ ОШИБКА: Ключ GOOGLE_API_KEY не установлен!")
        return None
    except Exception as e:
        logging.error(f"Ошибка конфигурации Gemini API: {e}")
        return None
    
    if not model:
        return None

    prompt = PROMPT_TEMPLATE.format(
        phrase=phrase,
        keyword=keyword, 
        language=language, 
        target_language=target_language
    )
    logging.info(f"Отправка AI-запроса для фразы '{phrase}' с ключевым словом '{keyword}'...")

    try:
        response = await model.generate_content_async(prompt)
        raw_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(raw_text)
        logging.info(f"AI успешно сгенерировал данные для '{phrase}'.")
        
        # Сохраняем в кэш (async set, TTL 7 дней = 604800 сек)
        await redis_client.set(cache_key, json.dumps(data), ex=604800)
        return data
    except Exception as e:
        logging.error(f"Ошибка при работе с AI: {e}")
        return None
