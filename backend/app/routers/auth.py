from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services.auth_service import auth_service
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class InitData(BaseModel):
    init_data: str

@router.post("/telegram")
async def telegram_auth(data: InitData, db: AsyncSession = Depends(get_db)):
    try:
        return await auth_service.authenticate_telegram_user(db, data.init_data)
    except HTTPException as e:
        raise e