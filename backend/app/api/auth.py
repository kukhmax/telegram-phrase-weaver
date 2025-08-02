from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..core.database import get_db
from ..models.user import User
from datetime import datetime

router = APIRouter()

# Pydantic модели для запросов
class TelegramAuthData(BaseModel):
    telegram_id: int
    username: str = None
    first_name: str = None
    last_name: str = None
    language_code: str = "en"

class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: str = None
    first_name: str = None
    language_code: str
    
    class Config:
        from_attributes = True

@router.post("/telegram", response_model=UserResponse)
async def authenticate_telegram_user(
    auth_data: TelegramAuthData,
    db: Session = Depends(get_db)
):
    """
    Аутентификация пользователя через Telegram WebApp
    Пока что упрощенная версия без проверки подписи
    """
    
    # Ищем существующего пользователя
    user = db.query(User).filter(User.telegram_id == auth_data.telegram_id).first()
    
    if user:
        # Обновляем время последней активности
        user.last_active = datetime.utcnow()
        # Обновляем данные если они изменились
        user.username = auth_data.username
        user.first_name = auth_data.first_name
        user.last_name = auth_data.last_name
        user.language_code = auth_data.language_code
    else:
        # Создаем нового пользователя
        user = User(
            telegram_id=auth_data.telegram_id,
            username=auth_data.username,
            first_name=auth_data.first_name,
            last_name=auth_data.last_name,
            language_code=auth_data.language_code
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    
    return user

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    telegram_id: int,  # Пока что передаем как параметр, позже добавим JWT
    db: Session = Depends(get_db)
):
    """
    Получение информации о текущем пользователе
    """
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return user