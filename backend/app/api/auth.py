from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.auth import TelegramAuthRequest, AuthResponse, UserResponse, UserUpdateRequest
from app.services.auth_service import auth_service
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = structlog.get_logger()

@router.post("/telegram", response_model=AuthResponse)
async def authenticate_telegram(
    auth_request: TelegramAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user via Telegram WebApp init data
    
    This endpoint verifies the Telegram WebApp initialization data,
    creates or updates the user record, and returns a JWT access token.
    """
    try:
        logger.info("Telegram authentication attempt")
        
        # Authenticate and get user data
        auth_data = auth_service.authenticate_telegram_user(
            db=db,
            init_data=auth_request.init_data
        )
        
        logger.info(
            "Telegram authentication successful",
            user_id=auth_data["user"]["id"],
            telegram_id=auth_data["user"]["telegram_id"]
        )
        
        return AuthResponse(**auth_data)
        
    except HTTPException as e:
        logger.warning("Telegram authentication failed", error=e.detail)
        raise e
    except Exception as e:
        logger.error("Unexpected authentication error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service temporarily unavailable"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information
    """
    logger.info("User profile request", user_id=current_user.id)
    return UserResponse(**current_user.to_dict())

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user settings
    """
    logger.info(
        "User profile update request", 
        user_id=current_user.id,
        updates=user_update.dict(exclude_none=True)
    )
    
    # Update user data
    if user_update.language_code is not None:
        current_user.language_code = user_update.language_code
    
    if user_update.settings is not None:
        # Merge with existing settings
        current_settings = current_user.settings or {}
        current_settings.update(user_update.settings)
        current_user.settings = current_settings
    
    try:
        db.commit()
        db.refresh(current_user)
        
        logger.info("User profile updated successfully", user_id=current_user.id)
        return UserResponse(**current_user.to_dict())
        
    except Exception as e:
        db.rollback()
        logger.error("Failed to update user profile", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )

@router.delete("/me")
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user account and all associated data
    """
    logger.warning("User account deletion request", user_id=current_user.id)
    
    try:
        # Delete user (cascading will handle related data)
        db.delete(current_user)
        db.commit()
        
        logger.info("User account deleted successfully", user_id=current_user.id)
        return {"message": "Account deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error("Failed to delete user account", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )