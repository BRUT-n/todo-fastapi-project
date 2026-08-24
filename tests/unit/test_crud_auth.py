import pytest
from src.auth.dependencies import get_user_status_by_token
from src.database.crud.auth import (  #get_user_by_email
    create_user,
    get_user_by_id,
    get_user_by_username,
)


@pytest.mark.asyncio(loop_scope="session")
async def test_create_user_success():
    # 1. Arrange: Создаем тестового пользователя
    user_data = {
        "username" : "UniqueUsername",
        "name": "UserName",
        "email": "usermail@email.com",
        "hashed_password": b"password_in_bytes"
    }

    # 2. Act: Вызываем тестируемую CRUD-функцию
    result = await create_user(**user_data)

    # 3. Assert: Проверяем результат
    assert result is not None
    assert isinstance(result.id_user, int)
    assert result.username == user_data["username"]
    assert result.email == user_data["email"]
    assert result.name == user_data["name"]
    assert result.hashed_password == user_data["hashed_password"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_by_username(create_test_user):
    # 1. Arrange: Создаем тестового пользователя
    existing_user = create_test_user
    users_username = existing_user.username

    result = await get_user_by_username(users_username)

    assert result is not None
    assert result.username == existing_user.username
    assert result.name == existing_user.name
    assert result.hashed_password == existing_user.hashed_password


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_by_username_not_found():
    # Act: Ищем несуществующего пользователя
    result = await get_user_by_username("WrongUsername")

    # Assert: Функция должна вернуть None
    assert result is None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_by_id_success(create_test_user):
    existing_user = create_test_user

    result = await get_user_by_id(user_id=existing_user.id_user)

    assert result is not None
    assert result.id_user == existing_user.id_user
    assert result.email == existing_user.email


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_by_id_not_found():
    result = await get_user_by_id(user_id=99999)

    assert result is None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_status_by_token_success(create_test_user):
    # 1. Arrange: Формируем payload, где sub — это строка с id_user
    existing_user = create_test_user
    payload = {"sub": str(existing_user.id_user)}

    # 2. Act: Передаем payload в нашу переписанную зависимость
    user = await get_user_status_by_token(payload=payload)

    # 3. Assert
    assert user is not None
    assert user.id_user == existing_user.id_user
