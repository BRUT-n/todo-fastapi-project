from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from src.config import settings

# postgres
engine = create_async_engine(settings.db.URL)

session_factory = async_sessionmaker(engine, expire_on_commit=False) # фабрика сессий на основе движка

class Base(DeclarativeBase):
    pass
