from datetime import timedelta

import pytest
from src.auth import exceptions
from src.auth.dependencies import (
    get_token_payload,
    get_user_status_by_token,
    register_user,
    validate_credentials,
)
from src.auth.schemas import UserRegisterSchema
from src.auth.utils import encode_jwt_token
from src.database.tables import UsersORM


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
    existing_user = create_test_user

    result = await validate_credentials(
        username=existing_user.username,
        password="secret_password"
    )

    assert result is not None
    assert result.id_user == existing_user.id_user


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
    """
    Успешное получение нагрузки из токена.
    """
    existing_token = encode_jwt_token(
        payload={"sub" : "UniqueSub"}
    )

    result = await get_token_payload(token=existing_token)

    assert result.get("sub") == "UniqueSub"
    assert result.get("exp") is not None
    assert result.get("iat") is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_token_payload_expired_failure():
    """
    Проверка ошибки истечения времени.
    Создается просроченный токен и ловит ошибку.
    """
    expired_token = encode_jwt_token(
        payload={"sub" : "UniqueSub"},
        expire_time_delta=timedelta(minutes=-5)
    )

    with pytest.raises(exceptions.TokenExpiredException):
        await get_token_payload(expired_token)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_token_payload_any_failure():
    """
    Проверка базовой ошибки если токен невалидный.
    Создается токен по неверному приватному ключу и ловит базовую ошибку.
    """
    invalid_token = "WrongToken"

    with pytest.raises(exceptions.TokenInvalidException):
        await get_token_payload(invalid_token)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_status_by_token_success(create_test_user: UsersORM):
    """
    Проверяется наличие юзера в БД по токену.
    """
    existing_user = create_test_user
    payload = {"sub" : str(existing_user.id_user)}

    result = await get_user_status_by_token(payload=payload)

    assert result is not None
    assert isinstance(result, UsersORM)
    assert result.id_user == existing_user.id_user


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_status_by_token_missing_sub():
    """
    Проверка ошибки отсутствия в токене поля sub.
    """
    payload = {"user_id" : "1"}

    with pytest.raises(exceptions.TokenMissingSubException):
        await get_user_status_by_token(payload=payload)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_status_by_token_invalid_sub_format():
    """
    Проверка ошибки неверного формата sub (не int).
    """
    # Arrange: В sub передали не число, а текст
    payload = {"sub": "not_an_int_id"}

    # Act & Assert: Должна выброситься ошибка невалидного токена
    with pytest.raises(exceptions.TokenInvalidException):
        await get_user_status_by_token(payload=payload)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_status_by_token_user_not_found():
    """
    Проверка ошибки отсутствия пользователя токена в БД.
    """
    payload = {"sub" : "99999"}

    with pytest.raises(exceptions.TokenUserNotFoundException):
        await get_user_status_by_token(payload=payload)
