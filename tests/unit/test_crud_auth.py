import pytest
from src.auth.dependencies import get_user_status_by_token
from src.database.crud.auth import create_user, get_user_by_email, get_user_by_id
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
async def test_get_user_by_email(create_test_user):
    # 1. Arrange: Создаем тестового пользователя
    existed_user = create_test_user
    users_email = existed_user.email

    result = await get_user_by_email(users_email)

    assert result is not None
    assert result.email == existed_user.email
    assert result.name == existed_user.name
    assert result.hashed_password == existed_user.hashed_password


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_by_email_not_found():
    # Act: Ищем несуществующего пользователя
    result = await get_user_by_email("wrong@example.com")

    # Assert: Функция должна вернуть None
    assert result is None

@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_by_id(create_test_user):
    existed_user = create_test_user

    result = await get_user_by_id(user_id=existed_user.id_user)

    assert result is not None
    assert result.id_user == existed_user.id_user
    assert result.email == existed_user.email

@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_by_id_not_found():
    result = await get_user_by_id(user_id=99999)

    assert result is None

@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_status_by_token_success(create_test_user):
    # 1. Arrange: Формируем payload, где sub — это строка с id_user
    existed_user = create_test_user
    payload = {"sub": str(existed_user.id_user)}

    # 2. Act: Передаем payload в нашу переписанную зависимость
    user = await get_user_status_by_token(payload=payload)

    # 3. Assert
    assert user is not None
    assert user.id_user == existed_user.id_user
