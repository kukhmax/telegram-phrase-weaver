from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date
from datetime import datetime, date
from app.database import Base

class TrainingSession(Base):
    __tablename__ = "training_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, default=date.today)
    cards_studied = Column(Integer, default=0)
    session_duration = Column(Integer, default=0)  # в секундах
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)