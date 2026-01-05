from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.core.config import settings

# Двигатель БД
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

# Асинхронная фабрика сессий
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Для зависимостей FastAPI
async def get_db():
    async with async_session_maker() as session:
        yield session