from os import stat
import jwt
from fastapi import Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.engine import result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import query

from src.auth import utils as auth_utils
from src.database import get_session
from src.models.todo_models import UsersORM
from src.auth.schemas import UserRegisterSchema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def register_user(
    user_data: UserRegisterSchema,
    session: AsyncSession = Depends(get_session)
) -> UsersORM:
    query = select(UsersORM).where(UsersORM.email == user_data.email)
    result = await session.execute(query)
    user = result.scalar_one_or_none() # проверка почты на уникальность в БД
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует"
        )

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


async def validate_auth_user(
    email: EmailStr = Form(),
    password: str = Form(),
    session: AsyncSession = Depends(get_session)
):
    unauth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный логин или пароль"
    )

    query = select(UsersORM).where(UsersORM.email == email)
    result = await session.execute(query)
    user = result.scalar_one_or_none

    if not user:
        raise unauth_error
    
    if not auth_utils.validate_password(
        password=password,
        hashed_password=user.hashed_password
    )


async def get_current_token_payload(
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
    except jwt.InvalidTokenError: # ловит базовое исключение Invalid
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_user(
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(get_session)
) -> UsersORM:
    """
    Проверяет наличие в БД юзера на основе данных из полезной нагрузки токена.
    Обращается напрямую к свежей БД для подтверждения доступа пользователя.
    """
    email = payload.get("sub") # найти уникальный емейл
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing sub"
        )

    query = select(UsersORM).where(UsersORM.email == email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user

