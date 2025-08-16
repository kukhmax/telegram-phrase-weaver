from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

Base = declarative_base()

# Lazy initialization to avoid issues during import
engine = None
async_session = None

def init_db():
    global engine, async_session
    if engine is None:
        settings = get_settings()
        engine = create_async_engine(settings.DATABASE_URL, echo=True)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    init_db()
    async with async_session() as session:
        yield session