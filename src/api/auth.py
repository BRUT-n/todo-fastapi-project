from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import utils as auth_utils
from src.auth.dependencies import (
    get_token_payload,
    get_user_status_by_token,
    register_user,
    validate_credentials,
)
from src.auth.schemas import (
    TokenInfo,
    UserAuthSchema,
    UserReadSchema,
    UserRegisterSchema,
)
from src.database.config import session_factory  #, get_session
from src.database.tables import UsersORM

router = APIRouter(prefix="/auth", tags=["Авторизация"])

@router.post(
    "/register",
    summary="Регистрация нового пользователя",
    response_model=UserReadSchema,
    status_code=status.HTTP_201_CREATED,
    )
async def register_new_user(
    user: UserRegisterSchema = Depends(register_user)
):
    return user

@router.post(
    "/login",
    summary="Вход с логином и паролем для получения токена (в том числе для сохранения в памяти приложения)",
    response_model=TokenInfo
    )
async def login_for_access_token(
    user: UsersORM = Depends(validate_credentials),
):

    jwt_payload = {
        "sub": user.email,
        "name": user.name,
        "user_id": user.id_user,
    }

    token = auth_utils.encode_jwt_token(jwt_payload)

    return TokenInfo(
        access_token=token,
        token_type="Bearer"
    )

@router.get(
    "/me",
    summary="Данные пользователя",
    response_model=UserReadSchema
)
async def get_me(
    user: UserReadSchema = Depends(get_user_status_by_token)
):
    return user
