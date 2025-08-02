import os
import google.generativeai as genai
import logging
import json
from typing import List, Dict, Optional
from ..core.config import settings

logger = logging.getLogger(__name__)

# Промпт для генерации фраз с изображениями
PROMPT_TEMPLATE = """
Твоя задача - помочь в изучении языков.
Для слова или фразы "{keyword}" на языке "{language}":
1. Придумай одно-два ключевых слова на английском для поиска картинки, которая лучше всего визуально ассоциируется с "{keyword}". Назови это поле "image_query".
2. Создай 5 реалистичных примеров предложений со словом "{keyword}". Используй разные грамматические формы.
3. Для каждого предложения предоставь точный перевод на {target_language} язык.
4. Критически важно: в каждом оригинальном предложении найди слово "{keyword}" (в любой его форме) и оберни его в HTML-теги <b> и </b>.
Верни ответ ТОЛЬКО в виде валидного JSON-объекта, без каких-либо других слов или форматирования.
Пример формата:
{{
  "image_query": "walking home sunset",
  "examples": [
    {{"original": "Eu estou <b>indo</b> para casa.", "translation": "Я иду домой."}},
    {{"original": "Eles <b>foram</b> para a praia.", "translation": "Они пошли на пляж."}}
  ]
}}
"""

class AIService:
    """
    Сервис для работы с AI API (Gemini)
    Генерирует фразы с ключевыми словами и поиском изображений
    """
    
    def __init__(self):
        # Конфигурация для Gemini API
        self.gemini_api_key = getattr(settings, 'gemini_api_key', None) or os.environ.get('GOOGLE_API_KEY')
        
        # Таймаут для запросов
        self.timeout = 30.0
    
    async def generate_phrases(
        self, 
        original_phrase: str, 
        keyword: str, 
        source_language: str, 
        target_language: str
    ) -> Dict[str, any]:
        """
        Генерирует 5 фраз с ключевым словом и поиском изображений
        
        Args:
            original_phrase: Исходная фраза на изучаемом языке
            keyword: Ключевое слово для вариаций
            source_language: Код исходного языка (например, 'en')
            target_language: Код целевого языка (например, 'ru')
            
        Returns:
            Словарь с ключами 'image_query' и 'examples'
        """
        try:
            # Используем новую архитектуру с Gemini
            result = await self._generate_with_gemini_new(
                keyword, source_language, target_language
            )
            if result:
                return result
            
            # Если AI недоступен, возвращаем mock данные
            logger.warning("AI сервис недоступен, используем mock данные")
            return self._generate_mock_data(keyword)
            
        except Exception as e:
            logger.error(f"Ошибка при генерации фраз: {e}")
            return self._generate_mock_data(keyword)
    
    async def _generate_with_gemini_new(
        self, 
        keyword: str, 
        language: str, 
        target_language: str
    ) -> Optional[Dict[str, any]]:
        """
        Генерирует примеры фраз с помощью Gemini AI, создавая новый клиент для каждого вызова.
        """
        
        # Создаем и настраиваем модель ВНУТРИ функции
        try:
            api_key = self.gemini_api_key or os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                logger.error("КРИТИЧЕСКАЯ ОШИБКА: Ключ GOOGLE_API_KEY не установлен!")
                return None
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
        except KeyError:
            logger.error("КРИТИЧЕСКАЯ ОШИБКА: Ключ GOOGLE_API_KEY не установлен!")
            return None
        except Exception as e:
            logger.error(f"Ошибка конфигурации Gemini API: {e}")
            return None
        
        if not model:
            return None

        prompt = PROMPT_TEMPLATE.format(
            keyword=keyword, 
            language=language, 
            target_language=target_language
        )
        logger.info(f"Отправка AI-запроса для '{keyword}'...")

        try:
            response = await model.generate_content_async(prompt)
            raw_text = response.text.strip().replace("```json", "").replace("```", "").strip()
            data = json.loads(raw_text)
            logger.info(f"AI успешно сгенерировал данные для '{keyword}'.")
            return data
        except Exception as e:
            logger.error(f"Ошибка при работе с AI: {e}")
            return None
    
    async def _generate_with_deepseek(
        self, 
        original_phrase: str, 
        keyword: str, 
        source_language: str, 
        target_language: str
    ) -> Optional[List[Dict[str, str]]]:
        """
        Генерация фраз через DeepSeek API
        """
        try:
            prompt = self._create_prompt(original_phrase, keyword, source_language, target_language)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.deepseek_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.deepseek_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                    return self._parse_ai_response(content)
                else:
                    logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"DeepSeek API request failed: {e}")
            return None
    
    async def _generate_with_gemini(
        self, 
        original_phrase: str, 
        keyword: str, 
        source_language: str, 
        target_language: str
    ) -> Optional[List[Dict[str, str]]]:
        """
        Генерация фраз через Gemini API
        """
        try:
            prompt = self._create_prompt(original_phrase, keyword, source_language, target_language)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.gemini_base_url}/models/gemini-pro:generateContent",
                    headers={
                        "Content-Type": "application/json"
                    },
                    params={
                        "key": self.gemini_api_key
                    },
                    json={
                        "contents": [
                            {
                                "parts": [
                                    {
                                        "text": prompt
                                    }
                                ]
                            }
                        ],
                        "generationConfig": {
                            "temperature": 0.7,
                            "maxOutputTokens": 1000
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data['candidates'][0]['content']['parts'][0]['text']
                    return self._parse_ai_response(content)
                else:
                    logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Gemini API request failed: {e}")
            return None
    
    def _create_prompt(
        self, 
        original_phrase: str, 
        keyword: str, 
        source_language: str, 
        target_language: str
    ) -> str:
        """
        Создает промпт для AI модели
        """
        language_names = {
            'en': 'английский',
            'ru': 'русский',
            'es': 'испанский',
            'fr': 'французский',
            'de': 'немецкий',
            'it': 'итальянский',
            'pt': 'португальский',
            'zh': 'китайский',
            'ja': 'японский',
            'ko': 'корейский'
        }
        
        source_lang_name = language_names.get(source_language, source_language)
        target_lang_name = language_names.get(target_language, target_language)
        
        return f"""Ты помощник для изучения языков. Твоя задача - создать 5 фраз на {source_lang_name} языке, используя ключевое слово "{keyword}" в разных грамматических формах (склонения, спряжения, времена).

Исходная фраза: "{original_phrase}"
Ключевое слово: "{keyword}"

Требования:
1. Создай 5 разных фраз на {source_lang_name} языке
2. В каждой фразе используй слово "{keyword}" в разной грамматической форме
3. Переведи каждую фразу на {target_lang_name} язык
4. Фразы должны быть полезными для изучения языка
5. Ответ должен быть в формате JSON

Формат ответа:
```json
[
  {{"original": "фраза на {source_lang_name}", "translation": "перевод на {target_lang_name}"}},
  {{"original": "фраза на {source_lang_name}", "translation": "перевод на {target_lang_name}"}},
  {{"original": "фраза на {source_lang_name}", "translation": "перевод на {target_lang_name}"}},
  {{"original": "фраза на {source_lang_name}", "translation": "перевод на {target_lang_name}"}},
  {{"original": "фраза на {source_lang_name}", "translation": "перевод на {target_lang_name}"}}
]
```

Верни только JSON без дополнительных комментариев."""
    
    def _parse_ai_response(self, content: str) -> List[Dict[str, str]]:
        """
        Парсит ответ от AI и извлекает JSON с фразами
        """
        try:
            # Ищем JSON в ответе
            start_idx = content.find('[') 
            end_idx = content.rfind(']') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                phrases = json.loads(json_str)
                
                # Валидируем структуру
                if isinstance(phrases, list) and len(phrases) > 0:
                    validated_phrases = []
                    for phrase in phrases:
                        if isinstance(phrase, dict) and 'original' in phrase and 'translation' in phrase:
                            validated_phrases.append({
                                'original': str(phrase['original']).strip(),
                                'translation': str(phrase['translation']).strip()
                            })
                    
                    if validated_phrases:
                        return validated_phrases[:5]  # Максимум 5 фраз
            
            # Если не удалось распарсить, возвращаем заглушку
            logger.warning("Failed to parse AI response, using fallback")
            return self._generate_mock_phrases("example phrase", "example")
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return self._generate_mock_phrases("example phrase", "example")
    
    def _generate_mock_phrases(self, original_phrase: str, keyword: str) -> List[Dict[str, str]]:
        """
        Генерирует заглушку для разработки и тестирования
        """
        return [
            {
                "original": f"I {keyword} every day",
                "translation": f"Я {keyword} каждый день"
            },
            {
                "original": f"She {keyword}s beautifully", 
                "translation": f"Она красиво {keyword}ет"
            },
            {
                "original": f"We {keyword}ed yesterday",
                "translation": f"Мы {keyword}али вчера"
            },
            {
                "original": f"They will {keyword} tomorrow",
                "translation": f"Они будут {keyword}ать завтра"
            },
            {
                "original": f"The {keyword}ing process is important",
                "translation": f"Процесс {keyword}ания важен"
            }
        ]
    
    def _generate_mock_data(self, keyword: str) -> Dict[str, any]:
        """
        Генерирует mock данные в новом формате с image_query и examples
        """
        return {
            "image_query": f"{keyword} activity",
            "examples": [
                {
                    "original": f"I <b>{keyword}</b> every day",
                    "translation": f"Я {keyword} каждый день"
                },
                {
                    "original": f"She <b>{keyword}s</b> beautifully", 
                    "translation": f"Она красиво {keyword}ет"
                },
                {
                    "original": f"We <b>{keyword}ed</b> yesterday",
                    "translation": f"Мы {keyword}али вчера"
                },
                {
                    "original": f"They will <b>{keyword}</b> tomorrow",
                    "translation": f"Они будут {keyword}ать завтра"
                },
                {
                    "original": f"The <b>{keyword}ing</b> was amazing",
                    "translation": f"{keyword.capitalize()}ание было потрясающим"
                }
            ]
        }

# Создаем экземпляр сервиса
ai_service = AIService()