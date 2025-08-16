from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

Base = declarative_base()

# Lazy initialization to avoid issues during import
engine = None
SessionLocal = None

def init_db():
    global engine, SessionLocal
    if engine is None:
        settings = get_settings()
        database_url = settings.DATABASE_URL
        
        # Ensure we use the correct psycopg2 URL format for sync
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        elif database_url.startswith("postgresql+asyncpg://"):
            database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        elif database_url.startswith("postgresql+psycopg://"):
            database_url = database_url.replace("postgresql+psycopg://", "postgresql://")
        
        engine = create_engine(database_url, echo=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()