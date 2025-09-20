#  backend/app/routers/cards.py

from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from typing import Optional
from app.services.enrichment import enrich_phrase, generate_audio
from app.services.simple_phrase_service import generate_simple_phrase_with_ai
import logging
import traceback

from app.schemas import CardCreate, Card as CardSchema
from app.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from app.models.deck import Deck
from app.models.card import Card
from app.models.user import User
from app.dependencies import get_current_user
from fastapi import HTTPException, status

router = APIRouter(prefix="/cards", tags=["cards"])

class EnrichRequest(BaseModel):
    phrase: str
    keyword: str
    lang_code: str
    target_lang: str

class AudioRequest(BaseModel):
    text: str
    lang_code: str

@router.post("/enrich")
async def enrich(request: EnrichRequest = Body(...)):
    """
    Роут для обогащения: POST body с данными → вызов enrich_phrase.
    """
    return await enrich_phrase(
        request.phrase, 
        request.keyword, 
        request.lang_code, 
        request.target_lang
    )

@router.post("/add-phrase")
async def add_phrase(request: EnrichRequest = Body(...)):
    """
    Роут для простого добавления фразы: POST body с данными → вызов generate_simple_phrase_with_ai.
    Возвращает только фразу с переводом, картинку и озвучку без дополнительных примеров.
    """
    try:
        result = await generate_simple_phrase_with_ai(
            request.phrase, 
            request.keyword, 
            request.lang_code, 
            request.target_lang
        )
        
        if result and "error" not in result:
            logging.info(f"Simple phrase generated successfully for '{request.phrase}'")
            return result
        else:
            error_msg = result.get("error", "Unknown error") if result else "AI service returned None"
            logging.error(f"Simple phrase generation failed: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Failed to generate simple phrase: {error_msg}")
            
    except Exception as e:
        logging.error(f"Exception in add_phrase endpoint: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/generate-audio")
async def generate_audio_endpoint(request: AudioRequest = Body(...)):
    """
    Генерирует аудио файл для текста и возвращает путь к файлу.
    """
    # Очищаем текст от HTML тегов
    clean_text = request.text.replace('<b>', '').replace('</b>', '')
    
    audio_path = await generate_audio(clean_text, request.lang_code, "phrase")
    
    if audio_path:
        # audio_path уже в формате "assets/audio/filename.mp3"
        # Преобразуем в полный URL для статических файлов
        if audio_path.startswith('assets/'):
            relative_path = f"/static/{audio_path}"
        else:
            # Fallback для старого формата
            import os
            filename = os.path.basename(audio_path)
            relative_path = f"/static/assets/audio/{filename}"
        return {"audio_url": relative_path}
    else:
        raise HTTPException(status_code=500, detail="Failed to generate audio")

@router.get("/deck/{deck_id}")
def get_deck_cards(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получает все карточки для указанной колоды.
    """
    from app.services.card_service import card_service
    return card_service.get_deck_with_cards(deck_id, current_user, db)

@router.post("/save", status_code=status.HTTP_201_CREATED)
def save_card(
    card_data: CardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Saves a new card to a specified deck.
    """
    from app.services.card_service import card_service
    return card_service.create_card(card_data, current_user, db)

class CardStatusUpdate(BaseModel):
    card_id: int
    rating: str  # "again", "good", "easy"

@router.post("/update-status")
def update_card_status(
    status_data: CardStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновляет статус карточки после тренировки.
    """
    from app.services.card_service import card_service
    return card_service.update_card_status(
        status_data.card_id, 
        status_data.rating, 
        current_user, 
        db
    )

@router.delete("/delete/{card_id}")
def delete_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удаляет карточку из базы данных.
    """
    from app.services.card_service import card_service
    return card_service.delete_card(card_id, current_user, db)