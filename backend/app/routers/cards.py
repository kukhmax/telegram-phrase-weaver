#  backend/app/routers/cards.py

from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from typing import Optional
from app.services.enrichment import enrich_phrase, generate_audio
import logging
import traceback

from app.schemas import CardCreate, Card as CardSchema
from app.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from app.models.deck import Deck
from app.models.card import Card
from app.models.user import User
# Создаем асинхронную версию get_current_user
from fastapi.security import OAuth2PasswordBearer
from ..services.auth_service import auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_current_user_sync(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Async dependency to get current user from JWT token.
    """
    try:
        payload = auth_service.verify_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials, user_id missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except HTTPException as e:
        raise e

    # Используем синхронный запрос
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    return user
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
def get_deck_cards(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Получает все карточки для указанной колоды.
    """
    # Проверяем, что колода принадлежит пользователю
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    if deck.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this deck")
    
    # Получаем карточки колоды
    cards = db.query(Card).filter(Card.deck_id == deck_id).order_by(Card.id).all()
    
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
            "next_review": card.due_date.isoformat() if card.due_date else None,
            "image_path": card.image_path
        } for card in cards]
    }

@router.post("/save", status_code=status.HTTP_201_CREATED)
def save_card(
    card_data: CardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Saves a new card to a specified deck.
    """
    try:
        # 1. Проверяем, существует ли колода и принадлежит ли она пользователю
        deck = db.query(Deck).filter(Deck.id == card_data.deck_id).first()

        if not deck:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
        
        if deck.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add card to this deck")

        # 2. Создаем карточку
        # Маппим front_text и back_text на поля модели Card
        from datetime import datetime, timedelta, timezone
        
        # Парсим next_review если он передан
        due_date = datetime.utcnow() + timedelta(days=1)  # По умолчанию без timezone
        if card_data.next_review:
            try:
                # Парсим ISO строку и конвертируем в UTC
                parsed_date = datetime.fromisoformat(card_data.next_review.replace('Z', '+00:00'))
                # Убираем timezone info для совместимости с базой
                due_date = parsed_date.replace(tzinfo=None)
            except:
                # Используем значение по умолчанию без timezone
                due_date = datetime.utcnow() + timedelta(days=1)
        
        new_card = Card(
            deck_id=card_data.deck_id,
            phrase=card_data.front_text,
            translation=card_data.back_text,
            keyword="",  # Пока оставляем пустым
            audio_path=None,
            image_path=card_data.image_path,
            examples=None,
            due_date=due_date,
            interval=1.0,  # Интервал в днях
            ease_factor=2.5  # Коэффициент легкости
        )
        
        # 3. Добавляем карточку в сессию
        db.add(new_card)
        
        # 4. Обновляем счетчик в колоде
        deck.cards_count += 1
        
        # 5. Коммитим все изменения
        db.commit()
        db.refresh(new_card)
        
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
        # Логируем детальную информацию об ошибке
        error_msg = f"Error saving card: {str(e)}"
        logging.error(error_msg)
        logging.error(f"Traceback: {traceback.format_exc()}")
        logging.error(f"Card data: {card_data.dict()}")
        
        if db:
            try:
                db.rollback()
            except Exception as rollback_error:
                logging.error(f"Rollback failed: {str(rollback_error)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save card: {str(e)}"
        )