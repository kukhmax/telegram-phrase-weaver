from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.services.auth_service import auth_service
from pydantic import BaseModel
from app.models.user import User
from datetime import datetime
from app import schemas 

router = APIRouter(prefix="/auth", tags=["auth"])

# Создаем схему зависимости для получения текущего пользователя
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current user from JWT token"""
    try:
        payload = auth_service.verify_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except HTTPException as e:
        raise e

    user = db.get(User, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    return user

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