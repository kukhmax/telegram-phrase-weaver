from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), default="en")
    is_premium = Column(Boolean, default=False)
    is_bot = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now())
    settings = Column(JSON, default={})
    
    # Relationships
    decks = relationship("Deck", back_populates="user", cascade="all, delete-orphan")
    cards = relationship("Card", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    
    @property
    def full_name(self):
        """Get user's full name"""
        names = [self.first_name, self.last_name]
        return " ".join([name for name in names if name])
    
    @property
    def display_name(self):
        """Get best display name for user"""
        return self.full_name or self.username or f"User {self.telegram_id}"
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "language_code": self.language_code,
            "is_premium": self.is_premium,
            "display_name": self.display_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "settings": self.settings or {}
        }