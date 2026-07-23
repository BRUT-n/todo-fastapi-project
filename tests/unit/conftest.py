# session_factory() переопределить на тестовую базы через тест контейнеры
# для тестирования фукнций с привязкой к тестовой базе (круды)
from _pytest import scope
import pytest
import pytest_asyncio
import src.database.config
import src.database.crud.auth

# from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.database.config import Base
from testcontainers.postgres import PostgresContainer

from src.database.tables import UsersORM


@pytest.fixture(scope="session", autouse=True)
def postgres_container():
    """
    Запуск контейнера на всю серию (сессию) тестов.
    """
    with PostgresContainer("postgres:17-alpine") as db:
        yield db

@pytest_asyncio.fixture(scope="session")
async def test_engine(postgres_container):
    """Создание асинхронного движка и таблиц внутри контейнера на всю сессию тестов."""
    db_url = postgres_container.get_connection_url().replace("psycopg2", "asyncpg")
    print(db_url)
    engine = create_async_engine(db_url, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_connection(test_engine):
    """Открывает физическое новое соединение и запускает внешнюю транзакцию ДЛЯ КАЖДОГО ТЕСТА."""
    async with test_engine.connect() as conn:
        # Начинаем корневую транзакцию для ВСЕГО теста
        async with conn.begin() as transaction:
            yield conn
            # После выхода из теста откатываем транзакцию на соединении
            await transaction.rollback()

@pytest_asyncio.fixture(scope="function", autouse=True)
async def override_session_factory(test_connection, monkeypatch):
    """
    Привязывает фабрику сессий к ОДНОМУ текущему соединению одного теста.
    Подменяет фабрику в коде приложения.
    """
    # ВАЖНО: bind=test_connection (а не engine!)
    test_session_factory = async_sessionmaker(
        bind=test_connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint"  # Заставляет commit() превращаться в SAVEPOINT
    )

    # Подменяем фабрику во всех модулях приложения
    monkeypatch.setattr("src.database.config.session_factory", test_session_factory)
    monkeypatch.setattr("src.database.crud.users.session_factory", test_session_factory)
    monkeypatch.setattr("src.database.crud.auth.session_factory", test_session_factory)

    yield test_session_factory


@pytest_asyncio.fixture(scope="function")
async def session(override_session_factory):
    """
    Фикстура для использования сессии прямо внутри кода тестов.
    На каждый тест своя сессия.
    """
    async with override_session_factory() as session:
        yield session



@pytest_asyncio.fixture(scope="function")
async def create_test_user(session):
    """
    Фикстура создания пользователя в БД для тестов.
    """
    user = UsersORM(
        name="UserName",
        email="usermail@test.com",
        hashed_password=b"secret_password"
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user
