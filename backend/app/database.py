from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

Base = declarative_base()

# Lazy initialization to avoid issues during import
engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None

def init_db():
    global engine, async_engine, SessionLocal, AsyncSessionLocal
    if engine is None:
        settings = get_settings()
        database_url = settings.DATABASE_URL
        
        # Sync engine for migrations and simple operations
        sync_url = database_url
        if sync_url.startswith("postgres://"):
            sync_url = sync_url.replace("postgres://", "postgresql://", 1)
        elif sync_url.startswith("postgresql+asyncpg://"):
            sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql://")
        elif sync_url.startswith("postgresql+psycopg://"):
            sync_url = sync_url.replace("postgresql+psycopg://", "postgresql://")
        
        engine = create_engine(sync_url, echo=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Async engine for FastAPI endpoints (только для PostgreSQL)
        if not database_url.startswith("sqlite"):
            async_url = database_url
            if async_url.startswith("postgres://"):
                async_url = async_url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif async_url.startswith("postgresql://"):
                async_url = async_url.replace("postgresql://", "postgresql+asyncpg://")
            elif not async_url.startswith("postgresql+asyncpg://"):
                async_url = async_url.replace("postgresql+psycopg://", "postgresql+asyncpg://")
            
            async_engine = create_async_engine(async_url, echo=True)
            AsyncSessionLocal = async_sessionmaker(
                bind=async_engine,
                class_=AsyncSession,
                autocommit=False,
                autoflush=False
            )
        else:
            # Для SQLite не создаем асинхронный движок
            async_engine = None
            AsyncSessionLocal = None

# Sync version for migrations
def get_db():
    init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Async version for FastAPI endpoints
async def get_async_db():
    init_db()
    if AsyncSessionLocal is None:
        raise RuntimeError("AsyncSessionLocal is not initialized")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()