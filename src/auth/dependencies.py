import jwt  # используется pyjwt (см uv.lock)
from fastapi import Depends, Form
from fastapi.security import OAuth2PasswordBearer

from src.auth import utils as auth_utils
from src.auth.exceptions import (
    AlreadyRegisteredException,
    InvalidCredentialsException,
    TokenExpiredException,
    TokenInvalidException,
    TokenMissingSubException,
    TokenUserNotFoundException,
)
from src.auth.schemas import UserRegisterSchema
from src.database.crud import auth as auth_crud
from src.database.tables import UsersORM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def register_user(
    user_data: UserRegisterSchema,
) -> UsersORM:
    """
    Регистрация пользователя.
    Используя pydantic-схему регистрации пользователя принимает имя, username, почту, пароль.
    Проверяет в базе дублирование username.
    Хеширует полученный пароль и вносит его с данными в базу.
    """
    user = await auth_crud.get_user_by_username(user_data.username)
    if user:
        raise AlreadyRegisteredException()

    hashed_password_bytes = auth_utils.hash_password(user_data.password)

    new_user = await auth_crud.create_user(
        username=user_data.username,
        name=user_data.name,
        hashed_password=hashed_password_bytes,
        email=user_data.email,
        )

    return new_user


async def validate_credentials(
    username: str = Form(),
    password: str = Form(),
) -> UsersORM:
    """
    Логин пользователя.
    Принимает username и пароль, проверяет наличие в базе username, и хеш пароля.
    """

    user = await auth_crud.get_user_by_username(username)

    if not user:
        raise InvalidCredentialsException()

    if not auth_utils.validate_password(
        password=password,
        hashed_password=user.hashed_password
    ):
        raise InvalidCredentialsException()

    return user


async def get_token_payload(
    token: str = Depends(oauth2_scheme)
) -> dict:
    """
    Извлекает и проверяет полезную нагрузку JWT.
    Данные проверяются сразу и используются при необходимости без обращения в БД.
    """
    try:
        payload = auth_utils.decode_jwt_token(
            encoded_token=token,
            public_key=auth_utils.PUBLIC_KEY,
            algorithm=auth_utils.ALGORITHM
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException()
    except jwt.InvalidTokenError: # ловит базовое исключение Invalid
        raise TokenInvalidException()

async def get_user_status_by_token(
    payload: dict = Depends(get_token_payload),
) -> UsersORM:
    """
    Проверяет наличие в БД юзера на основе данных из полезной нагрузки токена.
    Обращается напрямую к свежей БД для подтверждения доступа пользователя.
    Необходим для дополнительной проверки юзера-статуса в БД по полю АЙДИ (не почты).
    """
    # использование уникального АЙДИ вместо емейла
    sub = payload.get("sub")
    if not sub:
        raise TokenMissingSubException()

    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        raise TokenInvalidException()

    user = await auth_crud.get_user_by_id(user_id=user_id)

    if user is None:
        raise TokenUserNotFoundException()

    return user
