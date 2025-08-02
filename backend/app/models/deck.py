from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class Deck(Base):
    """
    Модель колоды карточек для изучения языка
    
    Колода содержит набор карточек на определенную тему
    и связана с конкретным пользователем
    """
    __tablename__ = "decks"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    
    # Название колоды (например: "Базовые фразы для путешествий")
    name = Column(String(255), nullable=False)
    
    # Описание колоды (опционально)
    description = Column(Text, nullable=True)
    
    # Изучаемый язык (например: "en", "fr", "de")
    source_language = Column(String(10), nullable=False)
    
    # Язык перевода (например: "ru", "en")
    target_language = Column(String(10), nullable=False)
    
    # Связь с пользователем (владелец колоды)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Связи с другими моделями
    # Связь с пользователем (один пользователь может иметь много колод)
    user = relationship("User", back_populates="decks")
    
    # Связь с карточками (одна колода может содержать много карточек)
    # cards = relationship("Card", back_populates="deck", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Deck(id={self.id}, name='{self.name}', user_id={self.user_id})>"
    
    @property
    def card_count(self):
        """
        Возвращает количество карточек в колоде
        Будет реализовано после создания модели Card
        """
        # return len(self.cards) if self.cards else 0
        return 0  # Временная заглушка
    
    @property
    def cards_to_review(self):
        """
        Возвращает количество карточек, готовых к повторению
        Будет реализовано после создания системы интервального повторения
        """
        return 0  # Временная заглушка