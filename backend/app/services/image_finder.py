import os
import logging
import asyncio
from unsplash.api import Api
from unsplash.auth import Auth
from app.core.config import settings

# Setup auth глобально (client_id из env; Unsplash требует только access_key для public)
auth = Auth(client_id=settings.UNSPLASH_ACCESS_KEY, client_secret="", redirect_uri="", code="")
api = Api(auth)

async def find_image_via_api(query: str) -> str | None:
    """
    Находим изображение via Unsplash API (замена Pexels для большего лимита).
    Wrapper sync, так что используем run_in_executor для async.
    """
    loop = asyncio.get_running_loop()
    
    def search_sync():
        try:
            search_results = api.search.photos(query, page=1, per_page=1)
            if search_results and search_results['results']:
                # Берем первое фото, URL medium размера (или regular для качества)
                return search_results['results'][0]['urls']['regular']
            return None
        except Exception as e:
            logging.error(f"Unsplash API error: {e}")
            return None
    
    image_url = await loop.run_in_executor(None, search_sync)
    if image_url:
        logging.info(f"Found image via Unsplash: {image_url}")
    else:
        logging.warning(f"No image found for '{query}' via Unsplash.")
    return image_url