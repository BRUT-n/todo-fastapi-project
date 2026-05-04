from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select

# from src.api.dependencies import SessionDep
from src.auth.dependencies import get_user_status_by_token
from src.auth.schemas import UserReadSchema
from src.database.crud import users as users_crud
from src.models.schemas import (
    UserAddSchema,
    UserPatchSchema,
    UserResponseSchema,
    UserUpdateSchema,
)

router = APIRouter(prefix="/me", tags=["Личный кабинет"])


@router.patch(
    "/profile",
    summary="Редактировать имя или почту",
    status_code=status.HTTP_200_OK,
    response_model=UserResponseSchema,
) # заменяет указанные свойства
async def patch_me(
    data: UserPatchSchema,
    user: UserReadSchema = Depends(get_user_status_by_token)
):
    patched_user = await users_crud.patch_user(
        user_id=user.id_user,
        data=data,
    )
    return patched_user

@router.delete(
    "/profile",
    summary="Удалить аккаунт",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_me(user: UserReadSchema = Depends(get_user_status_by_token)):
    result = await users_crud.delete_user(
        user_id=user.id_user,
    )
    return result


# админские роуты
admin = APIRouter()


@admin.post(
    "/users",
    tags=["Admin"],
    summary="Добавление пользователя",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseSchema,
    )
async def create_user(
    user_in: UserAddSchema,
):
    new_user = await users_crud.add_user(user=user_in)
    return new_user

@admin.get(
    "/users",
    tags=["Admin"],
    summary="Вывести всех пользователей",
    status_code=status.HTTP_200_OK,
    response_model=list[UserResponseSchema] # лист потому что вывод на несколько юзеров
    )
async def get_users():
    users = await users_crud.get_users()
    return users

@admin.patch(
    "/users/{user_id}",
    tags=["Admin"],
    summary="Обновить часть данных пользователя",
    status_code=status.HTTP_200_OK,
    response_model=UserResponseSchema,
) # заменяет указанные свойства
async def patch_user(
    user_id: int,
    data: UserPatchSchema,
):
    patched_user = await users_crud.patch_user(
        user_id=user_id,
        data=data,
    )
    return patched_user

@admin.delete(
    "/users/{user_id}",
    tags=["Admin"],
    summary="Удалить пользователя",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(user_id: int):
    result = await users_crud.delete_user(
        user_id=user_id,
    )
    return result
