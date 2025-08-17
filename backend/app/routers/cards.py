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
        # Преобразуем абсолютный путь в URL для статических файлов
        # audio_path выглядит как "assets/audio/phrase_abc123.mp3"
        # Нужно преобразовать в "/static/assets/audio/phrase_abc123.mp3"
        import os
        filename = os.path.basename(audio_path)
        relative_path = f"/static/assets/audio/{filename}"
        return {"audio_url": relative_path}
    else:
        raise HTTPException(status_code=500, detail="Failed to generate audio")

@router.get("/deck/{deck_id}")
async def get_deck_cards(
    deck_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получает все карточки для указанной колоды.
    """
    # Проверяем, что колода принадлежит пользователю
    result = await db.execute(select(Deck).where(Deck.id == deck_id))
    deck = result.scalar_one_or_none()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    if deck.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this deck")
    
    # Получаем карточки колоды
    from sqlalchemy import select
    result = await db.execute(
        select(Card).where(Card.deck_id == deck_id).order_by(Card.id)
    )
    cards = result.scalars().all()
    
    return {
        "deck": {
            "id": deck.id,
            "name": deck.name,
            "lang_from": deck.lang_from,
            "lang_to": deck.lang_to,
            "cards_count": deck.cards_count
        },
        "cards": [{
            "id": card.id,
            "front_text": card.phrase,
            "back_text": card.translation,
            "difficulty": 1,  # Пока используем значение по умолчанию
            "next_review": card.due_date.isoformat() if card.due_date else None
        } for card in cards]
    }

@router.post("/save", status_code=status.HTTP_201_CREATED)
async def save_card(
    card_data: CardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Saves a new card to a specified deck.
    """
    try:
        # 1. Проверяем, существует ли колода и принадлежит ли она пользователю
        from sqlalchemy import select
        result = await db.execute(select(Deck).where(Deck.id == card_data.deck_id))
        deck = result.scalar_one_or_none()

        if not deck:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
        
        if deck.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add card to this deck")

        # 2. Создаем карточку
        # Маппим front_text и back_text на поля модели Card
        from datetime import datetime, timedelta
        
        # Парсим next_review если он передан
        due_date = datetime.utcnow() + timedelta(days=1)  # По умолчанию
        if card_data.next_review:
            try:
                due_date = datetime.fromisoformat(card_data.next_review.replace('Z', '+00:00'))
            except:
                pass  # Используем значение по умолчанию
        
        new_card = Card(
            deck_id=card_data.deck_id,
            phrase=card_data.front_text,
            translation=card_data.back_text,
            keyword="",  # Пока оставляем пустым
            audio_path=None,
            image_path=None,
            examples=None,
            due_date=due_date,
            interval=1.0,  # Интервал в днях
            ease_factor=2.5  # Коэффициент легкости
        )
        
        # 3. Обновляем счетчик в колоде
        deck.cards_count += 1
        
        db.add(new_card)
        await db.commit()
        await db.refresh(new_card)
        
        return {
            "id": new_card.id,
            "deck_id": new_card.deck_id,
            "front_text": new_card.phrase,
            "back_text": new_card.translation,
            "message": "Card saved successfully"
        }
    except HTTPException:
        # Перебрасываем HTTP исключения как есть
        raise
    except Exception as e:
        # Логируем и возвращаем общую ошибку для всех остальных исключений
        import logging
        logging.error(f"Error saving card: {str(e)}")
        if db:
            await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save card: {str(e)}"
        )