from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event

engine = create_async_engine("sqlite+aiosqlite:///todo_lists.db") # движок БД sqlite и асинхронный драйвер для него

# postgres

# Этот блок — КЛЮЧЕВОЙ для каскадного удаления в SQLite
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, _):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

new_session = async_sessionmaker(engine) # фабрика сессий на основе движка

async def get_session():
    async with new_session() as session:
        yield session

class Base(DeclarativeBase):
    pass
