# Файл: core/image_finder.py (ФИНАЛЬНАЯ ВЕРСИЯ v4)

import os
from pexels_api import API
import logging
import asyncio

try:
    PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]
    api = API(PEXELS_API_KEY)
    logging.info("Pexels API успешно настроен.")
except KeyError:
    logging.error("КРИТИЧЕСКАЯ ОШИБКА: Ключ PEXELS_API_KEY не установлен!")
    api = None

async def find_image_via_api(query: str) -> str | None:
    if not api: return None
    
    try:
        loop = asyncio.get_running_loop()
        def search_sync():
            # --- ИСПРАВЛЕНО ОКОНЧАТЕЛЬНО ПО ДОКУМЕНТАЦИИ ---
            search_results = api.search(query, page=1, results_per_page=1)
            # Результаты - это словарь. Нам нужен ключ 'photos'.
            photos = search_results.get('photos')
            if photos:
                # photos - это список. Берем первый элемент.
                # src - это словарь с разными размерами. Берем 'medium'.
                return photos[0].get('src', {}).get('medium')
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