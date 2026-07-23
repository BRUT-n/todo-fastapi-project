# import asyncio
# from typing import AsyncGenerator

# import pytest
# from httpx import ASGITransport, AsyncClient
# from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
# from testcontainers.postgres import PostgresContainer

# from src.config import settings
# from src.database.config import Base
# from src.main import app


# # @pytest.fixture(scope="session")
# # def event_loop():
# #     """
# #     Единственный цикл событий для всех тестов.
# #     Необходим, чтобы не делать под каждый тест отдельно.
# #     """
# #     policy = asyncio.get_event_loop_policy() # политика создания цикла (для кроссплатформенности и изоляции потоков)
# #     loop = policy.new_event_loop()
# #     yield loop
# #     loop.close()


# @pytest.fixture(autouse=True)
# def container_for_tests():
#     with PostgresContainer("postgres:17-alpine") as postgres:
#         # Testcontainers по дефолту возвращает url (postgresql+psycopg2://...)
#         # переход в новый асинхронный asyncpg
#         sync_url = postgres.get_connection_url()
#         async_url = sync_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")

#         # Передаем этот URL глобально в настройки проекта
#         settings.db.URL = async_url

#         # контейнер дальше для всех тестов
#         yield postgres
#     # Как только выполнение выйдет из блока 'with', контейнер САМ уничтожится

# @pytest.fixture
# def db_engine_test(container_for_tests):
#     """Движок на основе нового УРЛ для бд"""
#     engine = create_async_engine(settings.db.URL, echo=True)
#     yield engine

# @pytest.fixture
# async def init_tables(db_engine_test):
#     """Используя выделенный новый движок создает таблицы. После тестов удаляет."""
#     async with db_engine_test.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

#     yield

#     async with db_engine_test.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)


# @pytest.fixture(scope="function")
# async def db_session_test(db_engine_test):
#     """Создает чистую асинхронную сессию для каждого конкретного теста."""
#     # фабрика сессий
#     async_session_factory = async_sessionmaker(
#         bind=db_engine_test,
#         class_=AsyncSession,
#         expire_on_commit=False
#     )

#     async with async_session_factory() as session:
#         yield session
#         # После завершения теста откат изменений
#         await session.rollback()


# @pytest.fixture
# async def client() -> AsyncGenerator[AsyncClient, None]:
#     """
#     Асинхронный клиент для отправки запросов в FastAPI.
#     Асинхронно, чтобы не блокировать поток.
#     AsyncClient - имитирует действия (запросы, куки, заголовки)
#     ASGITransport - связывает клиент и приложение в оперативной памяти, без uvicorn
#     """
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
#         yield ac
