#  backend/app/routers/cards.py

from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from typing import Optional
from app.services.enrichment import enrich_phrase, generate_audio

from app.schemas import CardCreate, Card as CardSchema
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.deck import Deck
from app.models.card import Card
from app.models.user import User
from .decks import get_current_user # Импортируем нашу зависимость
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

@router.post("/generate-audio")
async def generate_audio_endpoint(request: AudioRequest = Body(...)):
    """
    Генерирует аудио файл для текста и возвращает путь к файлу.
    """
    # Очищаем текст от HTML тегов
    clean_text = request.text.replace('<b>', '').replace('</b>', '')
    
    audio_path = await generate_audio(clean_text, request.lang_code, "phrase")
    
    if audio_path:
        # Возвращаем относительный путь для frontend
        relative_path = audio_path.replace('assets/', '/static/assets/')
        return {"audio_url": relative_path}
    else:
        raise HTTPException(status_code=500, detail="Failed to generate audio")

@router.post("/save", response_model=CardSchema, status_code=status.HTTP_201_CREATED)
async def save_card(
    card_data: CardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Saves a new card to a specified deck.
    """
    # 1. Проверяем, существует ли колода и принадлежит ли она пользователю
    deck = await db.get(Deck, card_data.deck_id)  # Эффективный способ получить объект по его первичному ключу.

    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    
    if deck.user_id != current_user.id:  # Мы никогда не должны позволять пользователю записывать данные в чужие колоды.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add card to this deck")

    # 2. Создаем карточку
    new_card = Card(**card_data.model_dump())
    
    # 3. Обновляем счетчик в колоде
    deck.cards_count += 1   # Обновляем счетчик карточек в связанной колоде. SQLAlchemy отследит это изменение и сохранит его во время await db.commit().
    
    db.add(new_card)
    await db.commit()
    await db.refresh(new_card)
    
    return new_card