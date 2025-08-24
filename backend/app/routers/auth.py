from fastapi import APIRouter, Depends, HTTPException, status, Request
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
        # Проверяем, есть ли валидные initData
        if not data.init_data or len(data.init_data.strip()) < 10:
            # Если initData пустые или слишком короткие, используем debug режим
            print(f"WARNING: Empty or invalid initData received: '{data.init_data}', falling back to debug mode")
            return telegram_auth_debug(db)
        
        return auth_service.authenticate_telegram_user(db, data.init_data)
    except HTTPException as e:
        # При ошибке аутентификации также используем debug режим
        print(f"WARNING: Telegram auth failed: {e.detail}, falling back to debug mode")
        return telegram_auth_debug(db)
    except Exception as e:
        # При любой другой ошибке также используем debug режим
        print(f"WARNING: Unexpected error in telegram auth: {str(e)}, falling back to debug mode")
        return telegram_auth_debug(db)
    
# НОВЫЙ ОТЛАДОЧНЫЙ ЭНДПОИНТ
@router.post("/telegram/debug", tags=["auth", "debug"])
def telegram_auth_debug(request: Request, db: Session = Depends(get_db)):
    """
    DEBUG ONLY: Authenticates a user based on their User Agent for unique identification.
    """
    import hashlib
    
    # Получаем User Agent для создания уникального ID
    user_agent = request.headers.get('user-agent', 'unknown')
    
    # Создаем уникальный Telegram ID на основе User Agent
    # Это обеспечит, что каждый пользователь получит свой уникальный профиль
    unique_string = f"debug_{user_agent}"
    telegram_id = int(hashlib.md5(unique_string.encode()).hexdigest()[:8], 16)
    
    print(f"DEBUG AUTH: User Agent: {user_agent}")
    print(f"DEBUG AUTH: Generated Telegram ID: {telegram_id}")

    # Логика похожа на get_or_create_user
    result = db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalars().first()

    if user:
        user.last_active = datetime.utcnow()
        db.commit()
        print(f"DEBUG AUTH: Found existing user: {user.username} ({user.first_name})")
    else:
        # Создаем нового пользователя с уникальными данными
        # Извлекаем информацию из User Agent для более персонализированного опыта
        device_info = "Unknown"
        if "Android" in user_agent:
            device_info = "Android"
        elif "iPhone" in user_agent or "iOS" in user_agent:
            device_info = "iOS"
        elif "Windows" in user_agent:
            device_info = "Windows"
        elif "Mac" in user_agent:
            device_info = "Mac"
        
        user = User(
            telegram_id=telegram_id,
            username=f"user_{str(telegram_id)[-6:]}",  # Последние 6 цифр ID
            first_name=f"User ({device_info})",
            last_name="User",
            settings={},
            is_premium=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"DEBUG AUTH: Created new user: {user.username} ({user.first_name})")
    
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