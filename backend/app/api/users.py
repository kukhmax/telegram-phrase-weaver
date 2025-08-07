from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import structlog

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.auth import UserResponse
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])
logger = structlog.get_logger()

@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user statistics
    """
    logger.info("User stats request", user_id=current_user.id)
    
    try:
        # Calculate user statistics
        total_decks = len(current_user.decks) if current_user.decks else 0
        
        total_cards = 0
        cards_due_today = 0
        total_reviews = 0
        
        if current_user.cards:
            total_cards = len(current_user.cards)
            
            from datetime import date
            today = date.today()
            cards_due_today = len([card for card in current_user.cards if card.due_date <= today])
        
        if current_user.reviews:
            total_reviews = len(current_user.reviews)
        
        # Calculate study streak (simplified)
        study_streak = 0  # TODO: Implement proper streak calculation
        
        stats = {
            "total_decks": total_decks,
            "total_cards": total_cards,
            "cards_due_today": cards_due_today,
            "total_reviews": total_reviews,
            "study_streak": study_streak,
            "user_since": current_user.created_at.isoformat() if current_user.created_at else None,
            "last_active": current_user.last_active.isoformat() if current_user.last_active else None
        }
        
        logger.info("User stats calculated", user_id=current_user.id, stats=stats)
        return stats
        
    except Exception as e:
        logger.error("Failed to calculate user stats", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate statistics"
        )

@router.get("/activity")
async def get_user_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    Get recent user activity
    """
    logger.info("User activity request", user_id=current_user.id, limit=limit)
    
    try:
        # Get recent reviews
        recent_reviews = []
        if current_user.reviews:
            sorted_reviews = sorted(
                current_user.reviews,
                key=lambda r: r.reviewed_at,
                reverse=True
            )[:limit]
            
            recent_reviews = [
                {
                    "id": review.id,
                    "card_id": review.card_id,
                    "rating": review.rating,
                    "reviewed_at": review.reviewed_at.isoformat(),
                    "response_time_ms": review.response_time_ms
                }
                for review in sorted_reviews
            ]
        
        activity = {
            "recent_reviews": recent_reviews,
            "total_reviews_today": len([
                r for r in current_user.reviews 
                if r.reviewed_at.date() == current_user.last_active.date()
            ]) if current_user.reviews and current_user.last_active else 0
        }
        
        logger.info("User activity retrieved", user_id=current_user.id)
        return activity
        
    except Exception as e:
        logger.error("Failed to get user activity", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve activity"
        )