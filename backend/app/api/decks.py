from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from ..core.database import get_db
from ..models.deck import Deck
from ..models.user import User

router = APIRouter()

# Pydantic модели для запросов и ответов

class DeckCreate(BaseModel):
    """
    Модель для создания новой колоды
    """
    name: str = Field(..., min_length=1, max_length=255, description="Название колоды")
    description: Optional[str] = Field(None, max_length=1000, description="Описание колоды")
    source_language: str = Field(..., min_length=2, max_length=10, description="Изучаемый язык (например: en, fr, de)")
    target_language: str = Field(..., min_length=2, max_length=10, description="Язык перевода (например: ru, en)")

class DeckUpdate(BaseModel):
    """
    Модель для обновления существующей колоды
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Новое название колоды")
    description: Optional[str] = Field(None, max_length=1000, description="Новое описание колоды")
    source_language: Optional[str] = Field(None, min_length=2, max_length=10, description="Новый изучаемый язык")
    target_language: Optional[str] = Field(None, min_length=2, max_length=10, description="Новый язык перевода")

class DeckResponse(BaseModel):
    """
    Модель ответа с информацией о колоде
    """
    id: int
    name: str
    description: Optional[str]
    source_language: str
    target_language: str
    user_id: int
    card_count: int = Field(description="Количество карточек в колоде")
    cards_to_review: int = Field(description="Количество карточек к повторению")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DeckListResponse(BaseModel):
    """
    Модель ответа со списком колод
    """
    decks: List[DeckResponse]
    total: int = Field(description="Общее количество колод")

# API endpoints

@router.post("/", response_model=DeckResponse, status_code=status.HTTP_201_CREATED)
async def create_deck(
    deck_data: DeckCreate,
    user_id: int = Query(...),  # Пока передаем как параметр, позже добавим JWT аутентификацию
    db: Session = Depends(get_db)
):
    """
    Создание новой колоды карточек
    
    - **name**: Название колоды (обязательно)
    - **description**: Описание колоды (опционально)
    - **source_language**: Изучаемый язык (например: "en", "fr", "de")
    - **target_language**: Язык перевода (например: "ru", "en")
    """
    
    # Проверяем существование пользователя
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Создаем новую колоду
    new_deck = Deck(
        name=deck_data.name,
        description=deck_data.description,
        source_language=deck_data.source_language,
        target_language=deck_data.target_language,
        user_id=user_id
    )
    
    # Сохраняем в базе данных
    db.add(new_deck)
    db.commit()
    db.refresh(new_deck)
    
    return new_deck

@router.get("/", response_model=DeckListResponse)
async def get_user_decks(
    user_id: int,  # Пока передаем как параметр, позже добавим JWT аутентификацию
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получение списка колод пользователя
    
    - **skip**: Количество колод для пропуска (для пагинации)
    - **limit**: Максимальное количество колод в ответе
    """
    
    # Проверяем существование пользователя
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Получаем колоды пользователя с пагинацией
    decks = db.query(Deck).filter(Deck.user_id == user_id).offset(skip).limit(limit).all()
    
    # Подсчитываем общее количество колод
    total = db.query(Deck).filter(Deck.user_id == user_id).count()
    
    return DeckListResponse(decks=decks, total=total)

@router.get("/{deck_id}", response_model=DeckResponse)
async def get_deck(
    deck_id: int,
    user_id: int,  # Пока передаем как параметр, позже добавим JWT аутентификацию
    db: Session = Depends(get_db)
):
    """
    Получение информации о конкретной колоде
    
    - **deck_id**: ID колоды
    """
    
    # Ищем колоду, принадлежащую пользователю
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == user_id
    ).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Колода не найдена или не принадлежит пользователю"
        )
    
    return deck

@router.put("/{deck_id}", response_model=DeckResponse)
async def update_deck(
    deck_id: int,
    deck_data: DeckUpdate,
    user_id: int,  # Пока передаем как параметр, позже добавим JWT аутентификацию
    db: Session = Depends(get_db)
):
    """
    Обновление информации о колоде
    
    - **deck_id**: ID колоды
    - Можно обновить любые поля: name, description, source_language, target_language
    """
    
    # Ищем колоду, принадлежащую пользователю
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == user_id
    ).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Колода не найдена или не принадлежит пользователю"
        )
    
    # Обновляем только переданные поля
    update_data = deck_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deck, field, value)
    
    # Сохраняем изменения
    db.commit()
    db.refresh(deck)
    
    return deck

@router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deck(
    deck_id: int,
    user_id: int,  # Пока передаем как параметр, позже добавим JWT аутентификацию
    db: Session = Depends(get_db)
):
    """
    Удаление колоды
    
    - **deck_id**: ID колоды
    - Внимание: Удаление колоды также удалит все связанные карточки!
    """
    
    # Ищем колоду, принадлежащую пользователю
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == user_id
    ).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Колода не найдена или не принадлежит пользователю"
        )
    
    # Удаляем колоду (каскадное удаление карточек произойдет автоматически)
    db.delete(deck)
    db.commit()
    
    return None