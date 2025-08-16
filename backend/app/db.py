# This file is kept for backward compatibility
# All database functionality moved to app.database
from app.database import get_db, Base, engine, async_session

__all__ = ["get_db", "Base", "engine", "async_session"]