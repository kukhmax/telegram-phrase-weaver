from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app.services.auth_service import auth_service
from pydantic import BaseModel
from app.models.user import User
from datetime import datetime
from app import schemas 

router = APIRouter(prefix="/auth", tags=["auth"])

class InitData(BaseModel):
    init_data: str

@router.post("/telegram")
async def telegram_auth(data: InitData, db: AsyncSession = Depends(get_db)):
    try:
        return await auth_service.authenticate_telegram_user(db, data.init_data)
    except HTTPException as e:
        raise e
    
# НОВЫЙ ОТЛАДОЧНЫЙ ЭНДПОИНТ
@router.post("/telegram/debug", tags=["auth", "debug"])
async def telegram_auth_debug(db: AsyncSession = Depends(get_db)):
    """
    DEBUG ONLY: Authenticates a predefined test user without initData verification.
    """
    # ID тестового пользователя. Можете выбрать любой, например, 12345678.
    DEBUG_TELEGRAM_ID = 12345678

    # Логика похожа на get_or_create_user
    result = await db.execute(select(User).where(User.telegram_id == DEBUG_TELEGRAM_ID))
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
    
    await db.commit()
    await db.refresh(user)

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