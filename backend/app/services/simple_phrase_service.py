import asyncio
import logging
import hashlib
import json
from typing import Optional
import google.generativeai as genai

from .utils import redis_client
from ..core.config import get_settings
from .image_finder import find_image_via_api
from .enrichment import download_and_save_image

settings = get_settings()

# Упрощенный промпт для генерации только одной фразы
SIMPLE_PHRASE_PROMPT = """
Your task is to help with language learning by creating a single phrase.
Given:
- Original phrase: "{phrase}" 
- Keyword to focus on: "{keyword}"
- Language: "{language}"
- Target language for translation: "{target_language}"

Please:
1. Create an English search query (1-2 words) for finding an image that best visually represents the keyword "{keyword}". Call this field "image_query".
2. Take the original phrase "{phrase}" and provide its accurate translation to {target_language}. In the original phrase, wrap the keyword "{keyword}" (in any of its forms) with HTML tags <b> and </b>.
3. In the translation, also wrap the translated keyword with HTML tags <b> and </b>.

Return ONLY a valid JSON object without any other words or formatting.
Format example:
{{
  "image_query": "walking home sunset",
  "phrase": {{
    "original": "Eu estou <b>indo</b> para casa.",
    "translation": "Я <b>иду</b> домой."
  }}
}}
"""

async def generate_simple_phrase_with_ai(phrase: str, keyword: str, language: str, target_language: str) -> dict:
    """
    Генерирует простую фразу с переводом с помощью AI.
    """
    
    # Проверяем, если это development режим с dummy ключом
    if settings.GOOGLE_API_KEY == "dummy_key_for_dev" or settings.ENVIRONMENT == "development":
        logging.info(f"🔧 Development mode: returning mock data for phrase '{phrase}'")
        return {
            "image_query": f"{keyword} concept",
            "phrase": {
                "original": f"{phrase.replace(keyword, f'<b>{keyword}</b>')}",
                "translation": f"Перевод: {phrase.replace(keyword, f'<b>{keyword}</b>')}"
            },
            "audio_url": None,
            "image_url": None,
            "image_path": None
        }
    
    # Ключ кэша: hash от phrase + keyword + "simple" для uniqueness
    cache_key = f"ai_simple:{hashlib.md5((phrase + keyword + 'simple').encode()).hexdigest()}"
    
    # Проверяем кэш (async get) с обработкой ошибок Redis
    try:
        cached = await redis_client.get(cache_key)
        if cached:
            logging.info(f"Simple AI data loaded from cache for '{phrase}'")
            return json.loads(cached)
    except Exception as e:
        logging.warning(f"Redis connection failed, proceeding without cache: {e}")
    
    # Если нет кэша — настройка модели
    try:
        api_key = settings.GOOGLE_API_KEY
        if not api_key or api_key.strip() == "":
            logging.error("КРИТИЧЕСКАЯ ОШИБКА: Ключ GOOGLE_API_KEY пустой или не установлен!")
            return {"error": "AI сервис недоступен: не настроен API ключ"}
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        logging.info(f"Google AI модель успешно настроена для простой фразы '{phrase}'")
    except AttributeError:
        logging.error("КРИТИЧЕСКАЯ ОШИБКА: Ключ GOOGLE_API_KEY не найден в настройках!")
        return {"error": "AI сервис недоступен: отсутствует API ключ в конфигурации"}
    except Exception as e:
        logging.error(f"Ошибка конфигурации Gemini API: {e}")
        return {"error": f"AI сервис недоступен: ошибка конфигурации - {str(e)}"}
    
    if not model:
        return None

    prompt = SIMPLE_PHRASE_PROMPT.format(
        phrase=phrase,
        keyword=keyword, 
        language=language, 
        target_language=target_language
    )
    logging.info(f"Отправка простого AI-запроса для фразы '{phrase}' с ключевым словом '{keyword}'...")

    try:
        response = await model.generate_content_async(prompt)
        
        if not response or not response.text:
            logging.error(f"AI вернул пустой ответ для простой фразы '{phrase}'")
            return {"error": "AI сервис вернул пустой ответ"}
        
        raw_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        
        # ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ ДЛЯ ОТЛАДКИ
        logging.info(f"🔍 ПОЛНЫЙ СЫРОЙ ОТВЕТ GEMINI для простой фразы '{phrase}':")
        logging.info(f"📄 RAW JSON: {raw_text}")
        logging.info(f"📏 Длина ответа: {len(raw_text)} символов")
        
        try:
            data = json.loads(raw_text)
            logging.info(f"✅ JSON успешно распарсен для простой фразы '{phrase}'")
            logging.info(f"🔑 Ключи в JSON: {list(data.keys())}")
        except json.JSONDecodeError as e:
            logging.error(f"❌ Ошибка парсинга JSON ответа AI для простой фразы '{phrase}': {e}")
            logging.error(f"🔍 Сырой ответ AI (первые 500 символов): {raw_text[:500]}")
            logging.error(f"🔍 Сырой ответ AI (последние 200 символов): {raw_text[-200:]}")
            return {"error": "AI сервис вернул некорректный формат данных"}
        
        logging.info(f"🎉 AI успешно сгенерировал простую фразу для '{phrase}'.")
        
        # ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ СТРУКТУРЫ ДАННЫХ
        logging.info(f"📊 АНАЛИЗ СТРУКТУРЫ JSON для простой фразы '{phrase}':")
        
        if 'image_query' in data:
            logging.info(f"🖼️ Image query: '{data['image_query']}'")
        
        if 'phrase' in data:
            phrase_data = data['phrase']
            logging.info(f"📝 Phrase data:")
            logging.info(f"   - original: '{phrase_data.get('original', 'N/A')}'")
            logging.info(f"   - translation: '{phrase_data.get('translation', 'N/A')}'")
        
        # Проверяем на наличие ошибок в структуре
        missing_fields = []
        if 'image_query' not in data: missing_fields.append('image_query')
        if 'phrase' not in data: missing_fields.append('phrase')
        
        if missing_fields:
            logging.warning(f"⚠️ Отсутствуют поля в JSON: {missing_fields}")
        else:
            logging.info(f"✅ Все обязательные поля присутствуют в JSON")
        
        # Сохраняем в кэш (async set, TTL 7 дней = 604800 сек)
        try:
            cache_saved = await redis_client.set(cache_key, json.dumps(data), ex=604800)
            if cache_saved:
                logging.info(f"💾 Данные для простой фразы '{phrase}' сохранены в кэш")
        except Exception as cache_error:
            logging.warning(f"⚠️ Не удалось сохранить в кэш: {cache_error}")
        
        # Добавляем обработку изображения
        image_path = None
        if 'image_query' in data and data['image_query']:
            try:
                logging.info(f"🖼️ Поиск изображения для запроса: '{data['image_query']}'")
                image_url = await find_image_via_api(data['image_query'])
                if image_url:
                    image_path = await download_and_save_image(image_url, data['image_query'])
                    if image_path:
                        logging.info(f"✅ Изображение успешно сохранено: {image_path}")
                    else:
                        logging.warning(f"⚠️ Не удалось сохранить изображение для '{data['image_query']}'")
                else:
                    logging.warning(f"⚠️ Изображение не найдено для запроса '{data['image_query']}'")
            except Exception as img_error:
                logging.error(f"❌ Ошибка при обработке изображения: {img_error}")
        
        # Добавляем путь к изображению в результат
        data['image_path'] = image_path
        
        return data
    except Exception as e:
        logging.error(f"Ошибка при работе с AI для простой фразы '{phrase}': {e}")
        return {"error": f"Ошибка AI сервиса: {str(e)}"}