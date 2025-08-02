# Импорт всех моделей для корректной работы SQLAlchemy relationships
from .user import User
from .deck import Deck

# Экспорт моделей для удобного импорта
__all__ = ["User", "Deck"]