import pytest
from src.auth import exceptions
from src.auth.dependencies import (
    get_user_status_by_token,
    register_user,
    validate_credentials,
)
from src.auth.schemas import UserRegisterSchema


@pytest.mark.asyncio(loop_scope="session")
async def test_register_user_success():
    user_data = UserRegisterSchema(
        username="Username",
        name="NewUserName",
        email="newemail@example.com",
        password="secret_password_string"
    )

    result = await register_user(user_data=user_data)

    assert result is not None
    assert result.email == "newemail@example.com"

@pytest.mark.asyncio(loop_scope="session")
async def test_register_user_already_registered(create_test_user):
    second_user_data = UserRegisterSchema(
        username="UniqueUsername",
        name="RegisterUserName",
        email="usermail@test.com",
        password="secret_password_string"
    )

    with pytest.raises(exceptions.AlreadyRegisteredException):
        await register_user(user_data=second_user_data)

@pytest.mark.asyncio(loop_scope="session")
async def test_validate_credentionals_success(create_test_user):
    existed_user = create_test_user

    result = await validate_credentials(
        username=existed_user.username,
        password="secret_password"
    )

    assert result is not None
    assert result.id_user == existed_user.id_user

@pytest.mark.asyncio(loop_scope="session")
async def test_validate_credentionals_invalid_email():
    with pytest.raises(exceptions.InvalidCredentialsException):
        await validate_credentials(username="WrongUsername", password="some_password")

@pytest.mark.asyncio(loop_scope="session")
async def test_validate_credentionals_wrong_password(create_test_user):
    existed_user_username = create_test_user.username
    with pytest.raises(exceptions.InvalidCredentialsException):
        await validate_credentials(username=existed_user_username, password="wrong_password")

@pytest.mark.asyncio(loop_scope="session")
async def test_get_token_payload_success():
    pass

# TODO дописать тесты для проверки нагрузки токена


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_status_by_token_invalid_sub_format():
    # Arrange: В sub передали не число, а текст (например, старый email)
    payload = {"sub": "not_an_int_id"}

    # Act & Assert: Должна выброситься ошибка невалидного токена
    with pytest.raises(exceptions.TokenInvalidException):
        await get_user_status_by_token(payload=payload)

# TODO дописать остальный сценарии для get_user_status_by_token
