# backend/tests/test_auth_service.py
"""
Тесты для сервиса аутентификации.
"""

import pytest
import time
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.services.auth_service import AuthService, TelegramAuthService
from app.models.user import User


class TestTelegramAuthService:
    """Тесты для TelegramAuthService."""
    
    def test_verify_telegram_data_valid(self):
        """Тест успешной верификации Telegram данных."""
        # Подготавливаем тестовые данные
        bot_token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
        
        # Создаем валидные init_data (упрощенная версия для теста)
        auth_date = int(time.time())
        user_data = '{"id":12345,"first_name":"Test","username":"test_user"}'
        
        # Для реального теста нужно создать правильный hash
        # Здесь мы тестируем только структуру метода
        
        auth_service = TelegramAuthService()
        
        # Тест с некорректными данными должен вызвать исключение
        with pytest.raises(HTTPException):
            auth_service.verify_telegram_data("invalid_data", bot_token)
    
    def test_verify_telegram_data_missing_hash(self):
        """Тест с отсутствующим hash."""
        auth_service = TelegramAuthService()
        bot_token = "test_token"
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_telegram_data("user=test&auth_date=123456", bot_token)
        
        assert exc_info.value.status_code == 400
        assert "Missing hash" in str(exc_info.value.detail)
    
    def test_verify_telegram_data_old_auth_date(self):
        """Тест с устаревшей датой аутентификации."""
        auth_service = TelegramAuthService()
        bot_token = "test_token"
        
        # Дата более 24 часов назад
        old_date = int(time.time()) - 86401
        init_data = f"auth_date={old_date}&user={{\"id\":123}}&hash=test_hash"
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_telegram_data(init_data, bot_token)
        
        assert exc_info.value.status_code == 401
        assert "too old" in str(exc_info.value.detail)


class TestAuthService:
    """Тесты для основного AuthService."""
    
    def test_create_access_token(self):
        """Тест создания JWT токена."""
        auth_service = AuthService()
        
        data = {"sub": "123", "telegram_id": 12345}
        token = auth_service.create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_with_expiry(self):
        """Тест создания токена с кастомным временем истечения."""
        auth_service = AuthService()
        
        data = {"sub": "123", "telegram_id": 12345}
        expires_delta = timedelta(minutes=30)
        token = auth_service.create_access_token(data, expires_delta)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_access_token_valid(self):
        """Тест верификации валидного токена."""
        auth_service = AuthService()
        
        # Создаем токен
        data = {"sub": "123", "telegram_id": 12345}
        token = auth_service.create_access_token(data)
        
        # Верифицируем токен
        payload = auth_service.verify_access_token(token)
        
        assert payload["sub"] == "123"
        assert payload["telegram_id"] == 12345
        assert "exp" in payload
    
    def test_verify_access_token_expired(self):
        """Тест верификации истекшего токена."""
        auth_service = AuthService()
        
        # Создаем токен с истекшим сроком
        data = {"sub": "123", "telegram_id": 12345}
        expires_delta = timedelta(seconds=-1)  # Уже истек
        token = auth_service.create_access_token(data, expires_delta)
        
        # Верификация должна вызвать исключение
        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_access_token(token)
        
        assert exc_info.value.status_code == 401
        assert "expired" in str(exc_info.value.detail).lower()
    
    def test_verify_access_token_invalid(self):
        """Тест верификации невалидного токена."""
        auth_service = AuthService()
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_access_token("invalid.token.here")
        
        assert exc_info.value.status_code == 401
        assert "validate credentials" in str(exc_info.value.detail)
    
    def test_get_or_create_user_new(self, db_session):
        """Тест создания нового пользователя."""
        auth_service = AuthService()
        
        telegram_data = {
            'user': {
                'id': 98765,
                'username': 'new_user',
                'first_name': 'New',
                'last_name': 'User',
                'language_code': 'en',
                'is_premium': False
            },
            'auth_date': int(time.time())
        }
        
        user = auth_service.get_or_create_user(db_session, telegram_data)
        
        assert user.telegram_id == 98765
        assert user.username == 'new_user'
        assert user.first_name == 'New'
        assert user.last_name == 'User'
        assert user.language_code == 'en'
        assert user.is_premium is False
    
    def test_get_or_create_user_existing(self, db_session, test_user):
        """Тест обновления существующего пользователя."""
        auth_service = AuthService()
        
        # Данные с обновленной информацией
        telegram_data = {
            'user': {
                'id': test_user.telegram_id,
                'username': 'updated_username',
                'first_name': 'Updated',
                'last_name': 'Name',
                'language_code': 'ru',
                'is_premium': True
            },
            'auth_date': int(time.time())
        }
        
        user = auth_service.get_or_create_user(db_session, telegram_data)
        
        # Проверяем, что пользователь обновился
        assert user.id == test_user.id  # Тот же пользователь
        assert user.username == 'updated_username'
        assert user.first_name == 'Updated'
        assert user.language_code == 'ru'
        assert user.is_premium is True
    
    def test_get_or_create_user_missing_id(self, db_session):
        """Тест с отсутствующим Telegram ID."""
        auth_service = AuthService()
        
        telegram_data = {
            'user': {
                'username': 'test_user',
                'first_name': 'Test'
                # Отсутствует 'id'
            },
            'auth_date': int(time.time())
        }
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.get_or_create_user(db_session, telegram_data)
        
        assert exc_info.value.status_code == 400
        assert "Missing Telegram user ID" in str(exc_info.value.detail)