from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, date, timedelta
from typing import List, Dict

from app.database import get_db
from app.models.user import User
from app.models.training_session import TrainingSession
from app.services.auth_service import auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_current_user_sync(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Sync dependency to get current user from JWT token.
    """
    try:
        payload = auth_service.verify_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

router = APIRouter(prefix="/training-stats", tags=["training-stats"])

@router.get("/daily")
def get_daily_training_stats(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Получает статистику ежедневных тренировок за указанное количество дней.
    """
    try:
        # Вычисляем диапазон дат
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # Получаем данные из базы
        training_data = db.query(
            TrainingSession.date,
            func.sum(TrainingSession.cards_studied).label('total_cards')
        ).filter(
            and_(
                TrainingSession.user_id == current_user.id,
                TrainingSession.date >= start_date,
                TrainingSession.date <= end_date
            )
        ).group_by(TrainingSession.date).all()
        
        # Создаем словарь для быстрого поиска
        data_dict = {item.date: item.total_cards for item in training_data}
        
        # Формируем результат для всех дней в диапазоне
        result = []
        current_date = start_date
        
        while current_date <= end_date:
            cards_studied = data_dict.get(current_date, 0)
            result.append({
                "date": current_date.isoformat(),
                "cardsStudied": cards_studied
            })
            current_date += timedelta(days=1)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get training statistics: {str(e)}"
        )

@router.post("/record")
def record_training_session(
    cards_studied: int,
    session_duration: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Записывает результаты тренировочной сессии.
    """
    try:
        today = date.today()
        
        # Проверяем, есть ли уже запись за сегодня
        existing_session = db.query(TrainingSession).filter(
            and_(
                TrainingSession.user_id == current_user.id,
                TrainingSession.date == today
            )
        ).first()
        
        if existing_session:
            # Обновляем существующую запись
            existing_session.cards_studied += cards_studied
            existing_session.session_duration += session_duration
            existing_session.updated_at = datetime.utcnow()
        else:
            # Создаем новую запись
            new_session = TrainingSession(
                user_id=current_user.id,
                date=today,
                cards_studied=cards_studied,
                session_duration=session_duration
            )
            db.add(new_session)
        
        db.commit()
        
        return {
            "message": "Training session recorded successfully",
            "date": today.isoformat(),
            "cards_studied": cards_studied
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record training session: {str(e)}"
        )