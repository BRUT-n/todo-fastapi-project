import pytest
from fastapi import status
from httpx import AsyncClient
from src.database.tables import UsersORM


@pytest.mark.asyncio(loop_scope="session")
async def test_register_success(ac: AsyncClient):
    """
    Проверка регистрации:
    Статус код верный.
    Ответ по схеме без чувствительных данных.
    Присвоен айди юзеру в формате инт.
    Данные указанные при регистрации записаны корректно.
    """
    payload = {
        "username": "UnuqueUsername",
        "name": "FirstName",
        "password": "secret_password",
    }

    response = await ac.post(
        "/auth/register",
        json=payload,
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    # assert UserReadSchema.model_validate(data)
    assert data["id_user"] is not None
    assert isinstance(data["id_user"], int)
    assert data["username"] == "UnuqueUsername"
    assert data["name"] == "FirstName"
    assert data["email"] is None


@pytest.mark.asyncio(loop_scope="session")
async def test_register_failure(ac: AsyncClient, create_test_user):
    """
    Проверка регистрации с уже существующим юзернейм.
    """
    existing_user_username = create_test_user.username

    payload = {
        "username": existing_user_username,
        "name": "AnotherName",
        "password": "another_secret_password",
    }

    response = await ac.post(
        "/auth/register",
        json=payload,
    )

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio(loop_scope="session")
async def test_login_for_access_token_success(
    ac: AsyncClient, create_test_user: UsersORM
):
    """
    Проверка логина по юзернейму и паролю на зарегистрированом в БД пользователе.
    """
    existing_user_username = create_test_user.username
    payload = {"username": existing_user_username, "password": "secret_password"}

    response = await ac.post("/auth/login", data=payload)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    # assert TokenInfo.model_validate(data)
    assert "access_token" in data
    assert data["token_type"] == "Bearer"
    assert len(data["access_token"]) > 100


@pytest.mark.asyncio(loop_scope="session")
async def test_login_for_access_token_wrong_password(
    ac: AsyncClient, create_test_user: UsersORM
):
    """
    Проверка ошибки неверного пароля.
    """
    existing_user_username = create_test_user.username
    payload = {"username": existing_user_username, "password": "WRONGpassword"}

    response = await ac.post("/auth/login", data=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio(loop_scope="session")
async def test_get_me_success(ac: AsyncClient, auth_header: dict, create_test_user):
    """
    Проверка доступа в личным данным авторизированного пользователя.
    """
    existing_user_id = create_test_user.id_user
    response = await ac.get(
        "/auth/me",
        headers=auth_header,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # assert UserReadSchema.model_validate(data)
    assert data["id_user"] == existing_user_id


@pytest.mark.asyncio(loop_scope="session")
async def test_get_me_unauthorized(ac: AsyncClient):
    """
    Проверка доступа в личным данным пользователя без авторизации.
    """
    response = await ac.get(
        "/auth/me",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
