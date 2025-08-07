import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from urllib.parse import parse_qsl

import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User

class TelegramAuthService:
    """Service for Telegram WebApp authentication"""
    
    @staticmethod
    def verify_telegram_data(init_data: str, bot_token: str) -> Dict[str, Any]:
        """
        Verify Telegram WebApp init data
        
        Args:
            init_data: Raw init data from Telegram WebApp
            bot_token: Telegram bot token
            
        Returns:
            Parsed and verified user data
            
        Raises:
            HTTPException: If verification fails
        """
        try:
            # Parse the init data
            parsed_data = dict(parse_qsl(init_data))
            
            # Extract hash and remove it from data
            received_hash = parsed_data.pop('hash', '')
            if not received_hash:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing hash in init data"
                )
            
            # Create data check string
            data_check_arr = []
            for key, value in sorted(parsed_data.items()):
                data_check_arr.append(f"{key}={value}")
            data_check_string = '\n'.join(data_check_arr)
            
            # Calculate expected hash
            secret_key = hmac.new(
                b"WebAppData", 
                bot_token.encode(), 
                hashlib.sha256
            ).digest()
            
            expected_hash = hmac.new(
                secret_key, 
                data_check_string.encode(), 
                hashlib.sha256
            ).hexdigest()
            
            # Verify hash
            if not hmac.compare_digest(received_hash, expected_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid hash - authentication failed"
                )
            
            # Check auth date (should be within 24 hours)
            auth_date = int(parsed_data.get('auth_date', 0))
            current_time = int(time.time())
            
            if current_time - auth_date > 86400:  # 24 hours
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication data is too old"
                )
            
            # Parse user data
            user_data = json.loads(parsed_data.get('user', '{}'))
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing user data"
                )
            
            return {
                'user': user_data,
                'auth_date': auth_date,
                'query_id': parsed_data.get('query_id'),
                'start_param': parsed_data.get('start_param')
            }
            
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user data format"
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to verify Telegram data: {str(e)}"
            )

class AuthService:
    """Main authentication service"""
    
    def __init__(self):
        self.telegram_auth = TelegramAuthService()
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)  # Default 24 hours
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm="HS256"
        )
        
        return encoded_jwt
    
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT access token"""
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def get_or_create_user(self, db: Session, telegram_data: Dict[str, Any]) -> User:
        """Get existing user or create new one from Telegram data"""
        user_info = telegram_data['user']
        telegram_id = user_info.get('id')
        
        if not telegram_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Telegram user ID"
            )
        
        # Try to find existing user
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if user:
            # Update user info and last active time
            user.username = user_info.get('username')
            user.first_name = user_info.get('first_name')
            user.last_name = user_info.get('last_name')
            user.language_code = user_info.get('language_code', 'en')
            user.is_premium = user_info.get('is_premium', False)
            user.is_bot = user_info.get('is_bot', False)
            user.last_active = datetime.utcnow()
            
            db.commit()
            db.refresh(user)
        else:
            # Create new user
            user = User(
                telegram_id=telegram_id,
                username=user_info.get('username'),
                first_name=user_info.get('first_name'),
                last_name=user_info.get('last_name'),
                language_code=user_info.get('language_code', 'en'),
                is_premium=user_info.get('is_premium', False),
                is_bot=user_info.get('is_bot', False),
                settings={}
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user
    
    def authenticate_telegram_user(self, db: Session, init_data: str) -> Dict[str, Any]:
        """Complete Telegram authentication flow"""
        if not settings.TELEGRAM_BOT_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Telegram bot token not configured"
            )
        
        # Verify Telegram data
        telegram_data = self.telegram_auth.verify_telegram_data(
            init_data, 
            settings.TELEGRAM_BOT_TOKEN
        )
        
        # Get or create user
        user = self.get_or_create_user(db, telegram_data)
        
        # Create access token
        access_token = self.create_access_token(
            data={
                "sub": str(user.id),
                "telegram_id": user.telegram_id,
                "username": user.username
            }
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.to_dict(),
            "expires_in": 86400  # 24 hours in seconds
        }

# Global auth service instance
auth_service = AuthService()