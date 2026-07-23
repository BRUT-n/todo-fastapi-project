import pytest
from src.database.crud.auth import create_user, get_user_by_email
from src.database.tables import UsersORM  # Ваша ORM модель


@pytest.mark.asyncio(loop_scope="session")
async def test_create_user():
    # 1. Arrange: Создаем тестового пользователя
    user_data = {
        "name": "UserName",
        "email": "usermail@email.com",
        "hashed_password": b"password_in_bytes"
    }

    # 2. Act: Вызываем тестируемую CRUD-функцию
    result = await create_user(**user_data)

    # 3. Assert: Проверяем результат
    assert result is not None
    assert isinstance(result.id_user, int)
    assert result.email == user_data["email"]
    assert result.name == user_data["name"]
    assert result.hashed_password == user_data["hashed_password"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_by_email():
    # 1. Arrange: Создаем тестового пользователя
    user_data = {
        "name": "UserName",
        "email": "usermail@email.com",
        "hashed_password": b"password_in_bytes"
    }

    # 2. Act: Вызываем тестируемую CRUD-функцию
    await create_user(**user_data)

    result = await get_user_by_email(user_data["email"])

    assert result is not None
    assert result.email == user_data["email"]
    assert result.name == user_data["name"]
    assert result.hashed_password == user_data["hashed_password"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_by_email_not_found():
    # Act: Ищем несуществующего пользователя
    result = await get_user_by_email("wrong@example.com")

    # Assert: Функция должна вернуть None
    assert result is None
