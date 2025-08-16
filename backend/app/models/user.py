from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    language_code = Column(String, default="en")
    is_premium = Column(Boolean, default=False)
    is_bot = Column(Boolean, default=False)
    last_active = Column(DateTime, default=datetime.utcnow)
    settings = Column(JSON, default={})