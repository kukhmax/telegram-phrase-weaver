# Импорт всех моделей для корректной работы SQLAlchemy relationships
from .user import User
from .deck import Deck
from .card import Card

# Экспорт моделей для удобного импорта
__all__ = ["User", "Deck", "Card"]