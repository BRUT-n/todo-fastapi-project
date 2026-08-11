import pytest
import pytest_asyncio
import src.database.config
import src.database.crud.auth
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.database.config import Base
from src.database.tables import ListsORM, TasksORM, UsersORM
from src.models.schemas import ListAddSchema, TaskAddSchema
from testcontainers.postgres import PostgresContainer


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

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
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

    # Подменяем фабрику во всех тестируемых модулях приложения
    monkeypatch.setattr("src.database.config.session_factory", test_session_factory)
    monkeypatch.setattr("src.database.crud.users.session_factory", test_session_factory)
    monkeypatch.setattr("src.database.crud.auth.session_factory", test_session_factory)
    monkeypatch.setattr("src.database.crud.todo_lists.session_factory", test_session_factory)
    monkeypatch.setattr("src.database.crud.tasks.session_factory", test_session_factory)

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

@pytest_asyncio.fixture(scope="function")
async def create_test_todo_list(session, create_test_user):
    """
    Фикстура создания листа задач в БД для тестов.
    Привязана к тестовому пользователю.
    """
    todo_lst = ListsORM(
        title="Title",
        description="Description",
        user_id=create_test_user.id_user
    )

    session.add(todo_lst)
    await session.commit()
    await session.refresh(todo_lst)

    return todo_lst

@pytest_asyncio.fixture(scope="function")
async def create_test_task(session, create_test_todo_list):
    """
    Фикстура создания задачи БД для тестов.
    Привязана к тестовому списку задач.
    """
    task = TasksORM(
        task_name="TaskName",
        completed=False,
        list_id=create_test_todo_list.id_list
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


