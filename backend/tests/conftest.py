# backend/tests/conftest.py
"""
Конфигурация для pytest.
Содержит фикстуры для тестирования.
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.models.user import User
from app.models.deck import Deck
from app.models.card import Card
from app.services.auth_service import auth_service

# Используем SQLite в памяти для тестов
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Создает event loop для всей сессии тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Создает тестовую сессию базы данных."""
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    # Создаем сессию
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Удаляем таблицы после теста
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Создает тестовый клиент FastAPI."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session) -> User:
    """Создает тестового пользователя."""
    user = User(
        telegram_id=12345678,
        username="test_user",
        first_name="Test",
        last_name="User",
        language_code="en",
        is_premium=False,
        settings={}
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_deck(db_session, test_user) -> Deck:
    """Создает тестовую колоду."""
    deck = Deck(
        user_id=test_user.id,
        name="Test Deck",
        description="Test deck for unit tests",
        lang_from="en",
        lang_to="ru",
        cards_count=0,
        due_count=0
    )
    db_session.add(deck)
    db_session.commit()
    db_session.refresh(deck)
    return deck


@pytest.fixture
def test_card(db_session, test_deck) -> Card:
    """Создает тестовую карточку."""
    card = Card(
        deck_id=test_deck.id,
        phrase="Hello world",
        translation="Привет мир",
        keyword="hello",
        audio_path=None,
        image_path=None,
        examples=None,
        interval=1.0,
        ease_factor=2.5
    )
    db_session.add(card)
    db_session.commit()
    db_session.refresh(card)
    return card


@pytest.fixture
def auth_token(test_user) -> str:
    """Создает JWT токен для тестового пользователя."""
    return auth_service.create_access_token(
        data={"sub": str(test_user.id), "telegram_id": test_user.telegram_id}
    )


@pytest.fixture
def auth_headers(auth_token) -> dict:
    """Создает заголовки авторизации для тестов."""
    return {"Authorization": f"Bearer {auth_token}"}