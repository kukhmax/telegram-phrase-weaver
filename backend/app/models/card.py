from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON
from datetime import datetime
from app.database import Base

class Card(Base):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("decks.id"))
    phrase = Column(String)
    translation = Column(String)
    keyword = Column(String)
    audio_path = Column(String)
    image_path = Column(String)
    examples = Column(JSON)  # List of additional examples
    due_date = Column(DateTime, default=datetime.utcnow)
    interval = Column(Float, default=1.0)  # Days
    ease_factor = Column(Float, default=2.5)