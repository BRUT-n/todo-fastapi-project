import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import utils as auth_utils
from src.database import get_session
from src.models.todo_models import UsersORM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

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
    except jwt.PyJWKError: # ловит базовое исключение (вместо Expired/Invalid)
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

