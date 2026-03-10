from fastapi import APIRouter, Depends, Form, HTTPException, status
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import utils as auth_utils
from src.auth.schemas import TokenInfo, UserReadSchema, UserRegisterSchema
from src.database import get_session
from src.models.todo_models import UsersORM
from src.auth.dependencies import register_user

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

@router.post("/login", summary="Вход с логином и паролем", response_model=TokenInfo)
async def login_for_access_token(
    email: EmailStr = Form(),
    password: str = Form(),
    session: AsyncSession = Depends(get_session)
):

    unauthorized_error = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль"
        )

    query = select(UsersORM).where(UsersORM.email == email) # вытащить в отдельную функцию
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    # круды вытащить в другой модуль

    if not user:
        raise unauthorized_error

    is_valid = auth_utils.validate_password(password, user.hashed_password)

    if not is_valid:
        raise unauthorized_error
    
    jwt_payload = {
        "sub": email,
        
    }

    # выделить отдельно
    token = auth_utils.encode_jwt_token(
        payload={"sub": email, "id": user.id},

    )