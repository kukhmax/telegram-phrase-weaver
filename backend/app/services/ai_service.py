import os
import hashlib
import json
import logging
from typing import Optional
import google.generativeai as genai

from .utils import redis_client
from ..core.config import get_settings

settings = get_settings()

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
3. Create a gap-fill version of the original phrase by replacing EXACTLY the keyword "{keyword}" (or its grammatical form that appears in the phrase) with "_____" (5 underscores). IMPORTANT: Replace only the specific word that corresponds to "{keyword}", not any other words. Call this "gap_fill".
4. Generate 5 additional realistic example sentences using the keyword "{keyword}" in different grammatical forms (conjugations, declensions, etc.).
5. For each of the 5 additional examples, provide accurate translations to {target_language}.
6. In each of the 5 additional examples, find and wrap the keyword "{keyword}" (in any of its forms) with HTML tags <b> and </b>.
7. For each of the 5 additional examples, create a gap-fill version by replacing EXACTLY the keyword "{keyword}" (or its grammatical form) with "_____" (5 underscores). IMPORTANT: Replace only the specific word that corresponds to "{keyword}", not any other words. Call this "gap_fill".

Return ONLY a valid JSON object without any other words or formatting.
Format example:
{{
  "image_query": "walking home sunset",
  "original_phrase": {{"original": "Eu estou <b>indo</b> para casa.", "translation": "Я иду домой.", "gap_fill": "Eu estou _____ para casa."}},
  "additional_examples": [
    {{"original": "Eles <b>vão</b> para a praia.", "translation": "Они идут на пляж.", "gap_fill": "Eles _____ para a praia."}},
    {{"original": "Nós <b>fomos</b> ao cinema.", "translation": "Мы пошли в кино.", "gap_fill": "Nós _____ ao cinema."}},
    {{"original": "Ela <b>vai</b> trabalhar.", "translation": "Она идет работать.", "gap_fill": "Ela _____ trabalhar."}},
    {{"original": "Vocês <b>foram</b> embora.", "translation": "Вы ушли.", "gap_fill": "Vocês _____ embora."}},
    {{"original": "Eu <b>irei</b> amanhã.", "translation": "Я пойду завтра.", "gap_fill": "Eu _____ amanhã."}}
  ]
}}
"""

async def generate_examples_with_ai(phrase: str, keyword: str, language: str, target_language: str) -> Optional[dict]:
    """
    Генерирует примеры фраз с помощью AI, включая исходную фразу и дополнительные примеры.
    """
    
   # Ключ кэша: hash от phrase + keyword для uniqueness
    cache_key = f"ai:{hashlib.md5((phrase + keyword).encode()).hexdigest()}"
    
    # Проверяем кэш (async get) с обработкой ошибок Redis
    try:
        cached = await redis_client.get(cache_key)
        if cached:
            logging.info(f"AI data loaded from cache for '{phrase}'")
            return json.loads(cached)
    except Exception as e:
        logging.warning(f"Redis connection failed, proceeding without cache: {e}")
    
    # Если нет кэша — настройка модели (как в оригинале)

    try:
        api_key = settings.GOOGLE_API_KEY
        if not api_key or api_key.strip() == "":
            logging.error("КРИТИЧЕСКАЯ ОШИБКА: Ключ GOOGLE_API_KEY пустой или не установлен!")
            return {"error": "AI сервис недоступен: не настроен API ключ"}
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        logging.info(f"Google AI модель успешно настроена для фразы '{phrase}'")
    except AttributeError:
        logging.error("КРИТИЧЕСКАЯ ОШИБКА: Ключ GOOGLE_API_KEY не найден в настройках!")
        return {"error": "AI сервис недоступен: отсутствует API ключ в конфигурации"}
    except Exception as e:
        logging.error(f"Ошибка конфигурации Gemini API: {e}")
        return {"error": f"AI сервис недоступен: ошибка конфигурации - {str(e)}"}
    
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
        
        if not response or not response.text:
            logging.error(f"AI вернул пустой ответ для фразы '{phrase}'")
            return {"error": "AI сервис вернул пустой ответ"}
        
        raw_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        
        # ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ ДЛЯ ОТЛАДКИ
        logging.info(f"🔍 ПОЛНЫЙ СЫРОЙ ОТВЕТ GEMINI для '{phrase}':")
        logging.info(f"📄 RAW JSON: {raw_text}")
        logging.info(f"📏 Длина ответа: {len(raw_text)} символов")
        
        try:
            data = json.loads(raw_text)
            logging.info(f"✅ JSON успешно распарсен для '{phrase}'")
            logging.info(f"🔑 Ключи в JSON: {list(data.keys())}")
        except json.JSONDecodeError as e:
            logging.error(f"❌ Ошибка парсинга JSON ответа AI для '{phrase}': {e}")
            logging.error(f"🔍 Сырой ответ AI (первые 500 символов): {raw_text[:500]}")
            logging.error(f"🔍 Сырой ответ AI (последние 200 символов): {raw_text[-200:]}")
            return {"error": "AI сервис вернул некорректный формат данных"}
        
        logging.info(f"🎉 AI успешно сгенерировал данные для '{phrase}'.")
        
        # ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ СТРУКТУРЫ ДАННЫХ
        logging.info(f"📊 АНАЛИЗ СТРУКТУРЫ JSON для '{phrase}':")
        
        if 'image_query' in data:
            logging.info(f"🖼️ Image query: '{data['image_query']}'")
        
        if 'original_phrase' in data:
            orig = data['original_phrase']
            logging.info(f"📝 Original phrase:")
            logging.info(f"   - original: '{orig.get('original', 'N/A')}'")
            logging.info(f"   - translation: '{orig.get('translation', 'N/A')}'")
            logging.info(f"   - gap_fill: '{orig.get('gap_fill', 'N/A')}'")
        
        if 'additional_examples' in data:
            examples = data['additional_examples']
            logging.info(f"📚 Additional examples ({len(examples)} штук):")
            for i, example in enumerate(examples[:3]):  # Показываем первые 3
                logging.info(f"   [{i+1}] original: '{example.get('original', 'N/A')}'")
                logging.info(f"   [{i+1}] translation: '{example.get('translation', 'N/A')}'")
                logging.info(f"   [{i+1}] gap_fill: '{example.get('gap_fill', 'N/A')}'")
        
        # Проверяем на наличие ошибок в структуре
        missing_fields = []
        if 'image_query' not in data: missing_fields.append('image_query')
        if 'original_phrase' not in data: missing_fields.append('original_phrase')
        if 'additional_examples' not in data: missing_fields.append('additional_examples')
        
        if missing_fields:
            logging.warning(f"⚠️ Отсутствуют поля в JSON: {missing_fields}")
        else:
            logging.info(f"✅ Все обязательные поля присутствуют в JSON")
        
        # Сохраняем в кэш (async set, TTL 7 дней = 604800 сек)
        try:
            cache_saved = await redis_client.set(cache_key, json.dumps(data), ex=604800)
            if cache_saved:
                logging.info(f"💾 Данные для '{phrase}' сохранены в кэш")
        except Exception as cache_error:
            logging.warning(f"⚠️ Не удалось сохранить в кэш: {cache_error}")
        
        return data
    except Exception as e:
        logging.error(f"Ошибка при работе с AI для фразы '{phrase}': {e}")
        return {"error": f"Ошибка AI сервиса: {str(e)}"}

if __name__ == "__main__":
    asyncio.run(generate_examples_with_ai('my dog', 'dog', 'en', 'pt'))
