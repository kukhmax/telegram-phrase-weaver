# backend/app/routers/decks.py

"""
Объяснение:
    get_current_user: Это функция-"зависимость" (dependency). FastAPI будет вызывать ее перед каждым эндпоинтом, где она указана. Она извлекает токен, проверяет его и загружает пользователя из БД. Это стандартный и безопасный способ защиты эндпоинтов.
    @router.post("/"): Создает новую колоду. Данные приходят в формате DeckCreate, а user_id берется из current_user.
    @router.get("/"): Возвращает список всех колод, принадлежащих текущему пользователю.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from ..database import get_db
from ..models.user import User
from ..models.deck import Deck
from ..models.card import Card
from ..schemas import DeckCreate, Deck as DeckSchema
from ..dependencies import get_current_user

router = APIRouter(prefix="/decks", tags=["decks"])


@router.post("/", response_model=DeckSchema, status_code=status.HTTP_201_CREATED)
def create_deck(
    deck_data: DeckCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new deck for the current user.
    """
    new_deck = Deck(
        **deck_data.model_dump(),
        user_id=current_user.id
    )
    db.add(new_deck)
    db.commit()
    db.refresh(new_deck)
    return new_deck


@router.get("/", response_model=List[DeckSchema])
def get_decks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Gets all decks for the current user, ordered by creation date (newest first).
    """
    result = db.execute(
        select(Deck)
        .where(Deck.user_id == current_user.id)
        .order_by(Deck.created_at.desc())
    )
    decks = result.scalars().all()
    return decks

@router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deck(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletes a deck by ID. Only the owner can delete their deck.
    """
    # Находим колоду
    result = db.execute(select(Deck).where(Deck.id == deck_id, Deck.user_id == current_user.id))
    deck = result.scalars().first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found or you don't have permission to delete it"
        )
    
    # Сначала удаляем все карточки этой колоды
    cards_result = db.execute(select(Card).where(Card.deck_id == deck_id))
    cards = cards_result.scalars().all()
    
    for card in cards:
        db.delete(card)
    
    # Теперь удаляем колоду
    db.delete(deck)
    db.commit()
    
    return None  # 204 No Content