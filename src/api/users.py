from fastapi import APIRouter, Depends, status

from src.auth.dependencies import get_user_status_by_token
from src.auth.exceptions import AlreadyRegisteredException
from src.auth.schemas import UserReadSchema
from src.database.crud import auth as auth_crud
from src.database.crud import users as users_crud
from src.models.schemas import (
    UserPatchSchema,
    UserResponseSchema,
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
    if data.username and data.username != user.username: # проверка уникальности username
        check_unique = await auth_crud.get_user_by_username(data.username)
        if check_unique:
            raise AlreadyRegisteredException()

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
    await users_crud.delete_user(
        user_id=user.id_user,
    )
    return None
