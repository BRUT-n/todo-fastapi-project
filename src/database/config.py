from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine("sqlite+aiosqlite:///todo_lists.db") # движок БД sqlite и асинхронный драйвер для него

# postgres

# Этот блок — КЛЮЧЕВОЙ для каскадного удаления в SQLite
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, _):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

session_factory = async_sessionmaker(engine, expire_on_commit=False) # фабрика сессий на основе движка

# async def get_session():
#     async with session_factory() as session:
#         yield session

class Base(DeclarativeBase):
    pass
