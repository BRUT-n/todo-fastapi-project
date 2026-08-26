import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.crud.auth import get_user_by_id
from src.database.tables import UsersORM


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_profile_success(ac:AsyncClient, auth_header: dict, create_test_user: UsersORM):
    """
    Проверка успешного редактирования профиля пользователя.
    """
    existing_user = create_test_user
    payload = {"username" : "new_unique_username"}

    response = await ac.patch(
        "/me/profile",
        json=payload,
        headers=auth_header
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    # assert UserResponseSchema.model_validate(data)
    assert data["username"] == "new_unique_username"
    assert data["id_user"] == existing_user.id_user


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_profile_username_already_registered(ac: AsyncClient, auth_header: dict, create_test_user: UsersORM, session: AsyncSession):
    """
    Проверка поменять юзернейм на уже зарегистрированный.
    """
    existing_user_of_token = create_test_user
    second_user = UsersORM(
        username="Username2",
        name="Name2",
        hashed_password=b"FakeHashedPassword"
    )
    session.add(second_user)
    await session.commit()

    payload = {"username" : "Username2"}

    response = await ac.patch(
        "/me/profile",
        json=payload,
        headers=auth_header
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Пользователь с таким username уже существует"


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_profile_unauthorized(ac: AsyncClient):
    """
    Проверка запрета на изменения без заголовка авторизации.
    """
    payload = {"name" : "some_name"}

    response = await ac.patch(
        "/me/profile",
        json=payload
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_profile_with_patch_schema_success(ac: AsyncClient, auth_header: dict, create_test_user: UsersORM):
    """
    Проверка успешной валидности данных по схеме
    """
    existing_user_of_token = create_test_user
    payload = {
        "username" : "NewUniqueUsername",
        "name" : "NewName",
        "email" : "new_valid_mail@test.com",
    }

    response = await ac.patch(
        "/me/profile",
        json=payload,
        headers=auth_header
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id_user"] == existing_user_of_token.id_user
    assert data["username"] == "NewUniqueUsername"
    assert data["name"] == "NewName"
    assert data["email"] == "new_valid_mail@test.com"


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    "bad_payload",
    [
        {"username" : "short"},
        {"name" : "n"},
        {"email" : "not_valid_mail"},
        {"extra_field" : "some_data"}
    ]
)
async def test_patch_profile_with_patch_schema_failed(ac: AsyncClient, auth_header: dict, bad_payload):
    """
    Параметризованная проверка невалидных данных для UserPatchSchema.
    """
    response = await ac.patch(
        "/me/profile",
        json=bad_payload,
        headers=auth_header
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "detail" in response.json()


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_user_success(ac: AsyncClient, auth_header: dict, create_test_user):
    """
    Проверка успешного удаления авторизованного пользователя.
    """
    existing_user_id = create_test_user.id_user

    response = await ac.delete(
        "/me/profile",
        headers=auth_header
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not response.content

    check_query = await get_user_by_id(user_id=existing_user_id)
    assert check_query is None


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_user_unauthorized(ac: AsyncClient):
    """
    Проверка ошибка удаления профиля без авторизации.
    """
    response = await ac.delete(
        "/me/profile",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
