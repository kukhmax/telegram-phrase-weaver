from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class Card(Base):
    """
    Модель карточки для изучения языка
    
    Карточка содержит текст на исходном языке (front_text),
    перевод на целевой язык (back_text), а также может включать
    аудио для произношения и изображение для визуального запоминания
    """
    __tablename__ = "cards"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    
    # Текст на исходном языке (лицевая сторона карточки)
    front_text = Column(Text, nullable=False)
    
    # Перевод на целевой язык (обратная сторона карточки)
    back_text = Column(Text, nullable=False)
    
    # URL аудиофайла для произношения front_text
    audio_url = Column(String(500), nullable=True)
    
    # URL изображения для визуального запоминания
    image_url = Column(String(500), nullable=True)
    
    # Уровень сложности карточки (1-5, где 1 - легкая, 5 - сложная)
    difficulty = Column(Integer, default=1, nullable=False)
    
    # Связь с колодой
    deck_id = Column(Integer, ForeignKey("decks.id"), nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Поля для системы интервального повторения (будут использоваться позже)
    # Количество правильных ответов подряд
    correct_streak = Column(Integer, default=0, nullable=False)
    
    # Дата следующего повторения
    next_review_date = Column(DateTime(timezone=True), nullable=True)
    
    # Интервал до следующего повторения (в днях)
    review_interval = Column(Float, default=1.0, nullable=False)
    
    # Связи с другими моделями
    # Связь с колодой (много карточек принадлежат одной колоде)
    deck = relationship("Deck", back_populates="cards")
    
    def __repr__(self):
        return f"<Card(id={self.id}, front='{self.front_text[:30]}...', deck_id={self.deck_id})>"
    
    @property
    def has_audio(self):
        """Проверяет, есть ли у карточки аудио"""
        return self.audio_url is not None and self.audio_url.strip() != ""
    
    @property
    def has_image(self):
        """Проверяет, есть ли у карточки изображение"""
        return self.image_url is not None and self.image_url.strip() != ""
    
    @property
    def is_due_for_review(self):
        """
        Проверяет, готова ли карточка к повторению
        Будет использоваться в системе интервального повторения
        """
        if self.next_review_date is None:
            return True
        return func.now() >= self.next_review_date
    
    def mark_as_correct(self):
        """
        Отмечает карточку как правильно отвеченную
        Увеличивает streak и интервал повторения
        """
        self.correct_streak += 1
        # Простая формула для увеличения интервала: новый_интервал = старый_интервал * 2
        self.review_interval = min(self.review_interval * 2, 30)  # Максимум 30 дней
        # Устанавливаем дату следующего повторения
        from datetime import datetime, timedelta
        self.next_review_date = datetime.utcnow() + timedelta(days=self.review_interval)
    
    def mark_as_incorrect(self):
        """
        Отмечает карточку как неправильно отвеченную
        Сбрасывает streak и уменьшает интервал
        """
        self.correct_streak = 0
        self.review_interval = 1.0  # Возвращаем к ежедневному повторению
        # Устанавливаем повторение на завтра
        from datetime import datetime, timedelta
        self.next_review_date = datetime.utcnow() + timedelta(days=1)