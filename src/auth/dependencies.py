import jwt
from fastapi import Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
from src.database.config import session_factory  #get_session
from src.database.tables import UsersORM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def register_user(
    user_data: UserRegisterSchema,
    # session: AsyncSession = Depends(get_session)
) -> UsersORM:
    """
    Регистрация пользователя.
    Используя pydantic-схему регистрации пользователя принимает имя, почту, пароль.
    Проверяет в базе дублирование почты.
    Хеширует полученный пароль и вносит его с данными в базу.
    """
    async with session_factory() as session:
        query = select(UsersORM).where(UsersORM.email == user_data.email)
        result = await session.execute(query)
        user = result.scalar_one_or_none() # проверка почты на уникальность в БД
        if user:
            raise AlreadyRegisteredException()

        hashed_password_bytes = auth_utils.hash_password(user_data.password)

        new_user = UsersORM(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password_bytes,
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user


async def validate_credentials(
    username: EmailStr = Form(),
    password: str = Form(),
    # session: AsyncSession = Depends(get_session)
) -> UsersORM:
    """
    Логин пользователя.
    Принимает почту и пароль, проверяет наличие в базе почты, и хеш пароля.
    """

    async with session_factory() as session:
        query = select(UsersORM).where(UsersORM.email == username)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

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
    # session: AsyncSession = Depends(get_session)
) -> UsersORM:
    """
    Проверяет наличие в БД юзера на основе данных из полезной нагрузки токена.
    Обращается напрямую к свежей БД для подтверждения доступа пользователя.
    Необходим для дополнительной проверки юзера-статуса в БД по полю почты.
    """
    email = payload.get("sub") # найти уникальный емейл
    if not email:
        raise TokenMissingSubException()

    async with session_factory() as session:
        query = select(UsersORM).where(UsersORM.email == email)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            raise TokenUserNotFoundException()

        return user
