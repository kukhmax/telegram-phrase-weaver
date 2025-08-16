from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Deck(Base):
    __tablename__ = "decks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    description = Column(String)
    lang_from = Column(String)
    lang_to = Column(String)
    cards_count = Column(Integer, default=0)
    due_count = Column(Integer, default=0)