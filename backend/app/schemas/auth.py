from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class TelegramAuthRequest(BaseModel):
    """Request model for Telegram authentication"""
    init_data: str = Field(..., description="Telegram WebApp init data string")
    
    class Config:
        schema_extra = {
            "example": {
                "init_data": "query_id=AAH...&user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22John%22%7D&auth_date=1234567890&hash=abc123..."
            }
        }

class UserResponse(BaseModel):
    """User information response"""
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    language_code: str
    is_premium: bool
    display_name: str
    created_at: Optional[str]
    last_active: Optional[str]
    settings: Dict[str, Any]
    
    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    """Authentication response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 86400,
                "user": {
                    "id": 1,
                    "telegram_id": 123456789,
                    "username": "john_doe",
                    "first_name": "John",
                    "last_name": "Doe",
                    "language_code": "en",
                    "is_premium": False,
                    "display_name": "John Doe",
                    "created_at": "2024-01-01T00:00:00",
                    "last_active": "2024-01-01T00:00:00",
                    "settings": {}
                }
            }
        }

class UserUpdateRequest(BaseModel):
    """Request to update user settings"""
    language_code: Optional[str] = Field(None, max_length=10)
    settings: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "language_code": "en",
                "settings": {
                    "theme": "dark",
                    "notifications": True
                }
            }
        }