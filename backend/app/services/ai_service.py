# Файл: core/ai_generator.py (ФИНАЛЬНАЯ АРХИТЕКТУРНАЯ ВЕРСИЯ)

import os
import google.generativeai as genai
import logging
import json
from typing import Optional

# Промпт может оставаться глобальным, это просто константа
PROMPT_TEMPLATE = """
Твоя задача - помочь в изучении языков. 
Для слова или фразы "{keyword}" на языке "{language}":
1.  Придумай одно-два ключевых слова на английском для поиска картинки, которая лучше всего визуально ассоциируется с "{keyword}". Назови это поле "image_query".
2.  Создай 5 реалистичных примеров предложений со словом "{keyword}". Используй разные грамматические формы.
3.  Для каждого предложения предоставь точный перевод на {target_language} язык.
4.  Критически важно: в каждом оригинальном предложении найди слово "{keyword}" (в любой его форме) и оберни его в HTML-теги <b> и </b>.
Верни ответ ТОЛЬКО в виде валидного JSON-объекта, без каких-либо других слов или форматирования.
Пример формата:
{{
  "image_query": "walking home sunset",
  "examples": [
    {{"original": "Eu estou <b>vou</b> em casa.", "translation": "Я иду домой."}},
    {{"original": "Eles <b>vão</b> para a praia.", "translation": "Они пошли на пляж."}}
  ]
}}
"""

async def generate_examples_with_ai(keyword: str, language: str, target_language: str) -> Optional[dict]:
    """
    Генерирует примеры фраз с помощью AI, создавая новый клиент для каждого вызова.
    """
    
    # logging.info(f"Отправка AI-запроса для '{keyword}'...")

    
    # --- КЛЮЧЕВОЕ АРХИТЕКТУРНОЕ ИСПРАВЛЕНИЕ ---
    # Мы создаем и настраиваем модель ВНУТРИ функции.
    # Это гарантирует, что для каждого асинхронного "движка" будет свой, свежий клиент.
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

    prompt = PROMPT_TEMPLATE.format(keyword=keyword, language=language, target_language=target_language)
    logging.info(f"Отправка AI-запроса для '{keyword}'...")

    try:
        response = await model.generate_content_async(prompt)
        raw_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(raw_text)
        logging.info(f"AI успешно сгенерировал данные для '{keyword}'.")
        return data
    except Exception as e:
        logging.error(f"Ошибка при работе с AI: {e}")
        return None