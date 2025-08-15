# backend/app/routers/decks.py

"""
Объяснение:
    get_current_user: Это функция-"зависимость" (dependency). FastAPI будет вызывать ее перед каждым эндпоинтом, где она указана. Она извлекает токен, проверяет его и загружает пользователя из БД. Это стандартный и безопасный способ защиты эндпоинтов.
    @router.post("/"): Создает новую колоду. Данные приходят в формате DeckCreate, а user_id берется из current_user.
    @router.get("/"): Возвращает список всех колод, принадлежащих текущему пользователю.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..db import get_db
from ..models.user import User
from ..models.deck import Deck
from ..schemas import DeckCreate, Deck as DeckSchema
from ..services.auth_service import auth_service

router = APIRouter(prefix="/decks", tags=["decks"])

# Создаем схему зависимости прямо здесь. Она будет ожидать токен в заголовке.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token") # tokenUrl здесь не используется, но обязателен

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """
    Dependency to get current user from JWT token.
    Provides more detailed error messages.
    """
    try:
        payload = auth_service.verify_access_token(token)
        # В токене мы сохраняем ID пользователя в поле 'sub' (subject)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials, user_id missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except HTTPException as e:
        # Пробрасываем ошибки от verify_access_token (например, истекший токен)
        raise e

    user = await db.get(User, int(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    return user


@router.post("/", response_model=DeckSchema, status_code=status.HTTP_201_CREATED)
async def create_deck(
    deck_data: DeckCreate,
    db: AsyncSession = Depends(get_db),
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
    await db.commit()
    await db.refresh(new_deck)
    return new_deck


@router.get("/", response_model=List[DeckSchema])
async def get_decks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Gets all decks for the current user.
    """
    result = await db.execute(select(Deck).where(Deck.user_id == current_user.id))
    decks = result.scalars().all()
    return decks