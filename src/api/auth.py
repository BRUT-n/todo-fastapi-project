from fastapi import APIRouter, Depends, Form, HTTPException, status
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import utils as auth_utils
from src.auth.dependencies import register_user, validate_auth_user
from src.auth.schemas import (
    TokenInfo,
    UserAuthSchema,
    UserReadSchema,
    UserRegisterSchema,
)
from src.crud import users
from src.database import get_session
from src.models.todo_models import UsersORM

router = APIRouter(prefix="/auth", tags=["Авторизация"])

@router.post(
    "/register",
    summary="Регистрация нового пользователя",
    response_model=UserReadSchema,
    )
async def register_new_user(
    user: UserRegisterSchema = Depends(register_user)
):
    return user

@router.post("/login",
    summary="Вход с логином и паролем для получения токена",
    response_model=TokenInfo
    )
async def login_for_access_token(
    user: UserAuthSchema = Depends(validate_auth_user),
):

    jwt_payload = {
        "sub": user.email,
    }

    token = auth_utils.encode_jwt_token(jwt_payload)

    return TokenInfo(
        access_token=token,
        token_type="Bearer"
    )
