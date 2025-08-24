from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.auth_service import auth_service
from app.models.user import User
from app.dependencies import get_current_user
from app import schemas 

router = APIRouter(prefix="/auth", tags=["auth"])

class InitData(BaseModel):
    init_data: str

@router.post("/telegram")
def telegram_auth(data: InitData, db: Session = Depends(get_db)):
    try:
        return auth_service.authenticate_telegram_user(db, data.init_data)
    except HTTPException as e:
        raise e
    
# НОВЫЙ ОТЛАДОЧНЫЙ ЭНДПОИНТ
@router.post("/telegram/debug", tags=["auth", "debug"])
def telegram_auth_debug(db: Session = Depends(get_db)):
    """
    DEBUG ONLY: Authenticates a predefined test user without initData verification.
    """
    # ID тестового пользователя. Можете выбрать любой, например, 12345678.
    DEBUG_TELEGRAM_ID = 12345678

    # Логика похожа на get_or_create_user
    result = db.execute(select(User).where(User.telegram_id == DEBUG_TELEGRAM_ID))
    user = result.scalars().first()

    if user:
        user.last_active = datetime.utcnow()
    else:
        user = User(
            telegram_id=DEBUG_TELEGRAM_ID,
            username="debug_user",
            first_name="Test",
            last_name="User",
            settings={},
            is_premium=False
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)

    # Создаем токен для этого пользователя
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "telegram_id": user.telegram_id}
    )

    user_schema = schemas.User.model_validate(user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_schema.model_dump()
    }

@router.get("/me")
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    user_schema = schemas.User.model_validate(current_user)
    return user_schema.model_dump()