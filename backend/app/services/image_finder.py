import os
import logging
import asyncio
from typing import Optional
from app.core.config import get_settings

settings = get_settings()

# Инициализация Pexels API
try:
    import requests
    PEXELS_API_KEY = settings.PEXELS_API_KEY
    if PEXELS_API_KEY and PEXELS_API_KEY != "your_pexels_api_key_here":
        logging.info("Pexels API успешно настроен.")
        pexels_available = True
    else:
        logging.warning("PEXELS_API_KEY не установлен или содержит placeholder.")
        pexels_available = False
except Exception as e:
    logging.error(f"Ошибка инициализации Pexels API: {e}")
    pexels_available = False

async def find_image_via_api(query: str) -> Optional[str]:
    """Поиск изображения через Pexels API"""
    if not pexels_available or not PEXELS_API_KEY:
        logging.warning("Pexels API недоступен")
        return None
    
    try:
        loop = asyncio.get_running_loop()
        
        def search_sync():
            headers = {
                'Authorization': PEXELS_API_KEY
            }
            
            params = {
                'query': query,
                'per_page': 1,
                'page': 1
            }
            
            response = requests.get(
                'https://api.pexels.com/v1/search',
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                photos = data.get('photos', [])
                if photos:
                    # Возвращаем URL изображения среднего размера
                    return photos[0]['src']['medium']
            elif response.status_code == 401:
                logging.error("Pexels API: Неверный API ключ")
            elif response.status_code == 429:
                logging.error("Pexels API: Превышен лимит запросов")
            else:
                logging.error(f"Pexels API error: {response.status_code}")
            
            return None
        
        image_url = await loop.run_in_executor(None, search_sync)
        
        if image_url:
            logging.info(f"Найдена картинка через Pexels API: {image_url}")
        else:
            logging.warning(f"Картинки для '{query}' через Pexels не найдены.")
            
        return image_url
        
    except Exception as e:
        logging.error(f"Ошибка при работе с Pexels API: {e}")
        return None