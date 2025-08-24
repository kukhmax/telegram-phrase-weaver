# backend/app/dependencies.py
"""
Общие зависимости для FastAPI эндпоинтов.
Централизованное место для функций аутентификации и авторизации.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from .database import get_db
from .models.user import User
from .services.auth_service import auth_service

# OAuth2 схема для получения токена из заголовка Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency для получения текущего пользователя из JWT токена.
    
    Args:
        token: JWT токен из заголовка Authorization
        db: Сессия базы данных
        
    Returns:
        User: Объект пользователя
        
    Raises:
        HTTPException: Если токен недействителен или пользователь не найден
    """
    try:
        # Верифицируем токен и извлекаем payload
        payload = auth_service.verify_access_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials: user_id missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except HTTPException:
        # Пробрасываем HTTP исключения от verify_access_token
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Получаем пользователя из базы данных
    user = db.get(User, int(user_id))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency для получения активного пользователя.
    Можно расширить проверками на блокировку аккаунта.
    
    Args:
        current_user: Текущий пользователь
        
    Returns:
        User: Активный пользователь
        
    Raises:
        HTTPException: Если пользователь неактивен
    """
    # Здесь можно добавить проверки на активность пользователя
    # Например, проверка поля is_active, is_banned и т.д.
    
    return current_user


def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency для получения пользователя, если токен предоставлен.
    Полезно для эндпоинтов, которые работают как с авторизованными,
    так и с неавторизованными пользователями.
    
    Args:
        token: Опциональный JWT токен
        db: Сессия базы данных
        
    Returns:
        Optional[User]: Пользователь или None
    """
    if not token:
        return None
        
    try:
        return get_current_user(token, db)
    except HTTPException:
        # Если токен недействителен, возвращаем None вместо ошибки
        return None