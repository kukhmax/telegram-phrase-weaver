from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, Date, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Deck(Base):
    """
    Модель колоды карточек для изучения языка
    
    Колода содержит набор карточек на определенную тему
    и связана с конкретным пользователем
    """
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source_lang = Column(String(10), nullable=False)
    target_lang = Column(String(10), nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="decks")
    concepts = relationship("Concept", back_populates="deck", cascade="all, delete-orphan")
    
    def to_dict(self, include_stats=False):
        """Convert deck to dictionary"""
        result = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "source_lang": self.source_lang,
            "target_lang": self.target_lang,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_stats:
            # Calculate stats
            total_concepts = len(self.concepts) if self.concepts else 0
            total_phrases = sum(len(concept.phrases) for concept in self.concepts) if self.concepts else 0
            total_cards = sum(len(phrase.cards) for concept in self.concepts for phrase in concept.phrases) if self.concepts else 0
            
            result.update({
                "stats": {
                    "total_concepts": total_concepts,
                    "total_phrases": total_phrases,
                    "total_cards": total_cards,
                    "cards_due_today": 0  # Will be calculated in service layer
                }
            })
        
        return result

class Concept(Base):
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False)
    keyword = Column(String(255), nullable=False)
    image_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    deck = relationship("Deck", back_populates="concepts")
    phrases = relationship("Phrase", back_populates="concept", cascade="all, delete-orphan")
    
    def to_dict(self, include_phrases=False):
        """Convert concept to dictionary"""
        result = {
            "id": self.id,
            "deck_id": self.deck_id,
            "keyword": self.keyword,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_phrases and self.phrases:
            result["phrases"] = [phrase.to_dict() for phrase in self.phrases]
        
        return result

class Phrase(Base):
    __tablename__ = "phrases"

    id = Column(Integer, primary_key=True, index=True)
    concept_id = Column(Integer, ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    audio_url = Column(Text, nullable=True)
    difficulty_level = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint('difficulty_level >= 1 AND difficulty_level <= 5', name='check_difficulty_level'),
    )
    
    # Relationships
    concept = relationship("Concept", back_populates="phrases")
    cards = relationship("Card", back_populates="phrase", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert phrase to dictionary"""
        return {
            "id": self.id,
            "concept_id": self.concept_id,
            "original_text": self.original_text,
            "translated_text": self.translated_text,
            "audio_url": self.audio_url,
            "difficulty_level": self.difficulty_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    phrase_id = Column(Integer, ForeignKey("phrases.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    card_type = Column(String(20), nullable=False)  # 'direct' or 'reverse'
    front_text = Column(Text, nullable=False)
    back_text = Column(Text, nullable=False)
    interval_days = Column(Integer, default=1)
    ease_factor = Column(Float, default=2.5)
    due_date = Column(Date, default=func.current_date())
    times_reviewed = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint("card_type IN ('direct', 'reverse')", name='check_card_type'),
    )
    
    # Relationships
    phrase = relationship("Phrase", back_populates="cards")
    user = relationship("User", back_populates="cards")
    reviews = relationship("Review", back_populates="card", cascade="all, delete-orphan")
    
    @property
    def accuracy(self):
        """Calculate accuracy percentage"""
        if self.times_reviewed == 0:
            return 0
        return round((self.times_correct / self.times_reviewed) * 100, 1)
    
    def to_dict(self):
        """Convert card to dictionary"""
        return {
            "id": self.id,
            "phrase_id": self.phrase_id,
            "card_type": self.card_type,
            "front_text": self.front_text,
            "back_text": self.back_text,
            "interval_days": self.interval_days,
            "ease_factor": self.ease_factor,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "times_reviewed": self.times_reviewed,
            "times_correct": self.times_correct,
            "accuracy": self.accuracy,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("cards.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1=again, 2=good, 3=easy
    response_time_ms = Column(Integer, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 3', name='check_rating'),
    )
    
    # Relationships
    card = relationship("Card", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    
    def to_dict(self):
        """Convert review to dictionary"""
        return {
            "id": self.id,
            "card_id": self.card_id,
            "rating": self.rating,
            "response_time_ms": self.response_time_ms,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }