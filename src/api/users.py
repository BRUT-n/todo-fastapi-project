from fastapi import APIRouter, HTTPException, status
from sqlalchemy import delete, select

# from src.api.dependencies import SessionDep
from src.database.config import Base, engine
from src.database.crud import users as users_crud
from src.database.tables import UsersORM
from src.models.schemas import (
    UserAddSchema,
    UserPatchSchema,
    UserResponseSchema,
    UserUpdateSchema,
)

router = APIRouter()

# @router.post(
#     "/database",
#     tags=["Взаимодейсвие с БД"]
#     ) # в лайфспан
# async def setup_database():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#     return {"ok": True, "message" : "Database droped and created again"}


@router.post(
    "/users", tags=["Пользователи"],
    summary="Добавление пользователя",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseSchema,
    )
async def create_user(
    user_in: UserAddSchema,
):
    new_user = await users_crud.add_user(user=user_in)
    return new_user


@router.get(
    "/users",
    tags=["Пользователи"],
    summary="Вывести всех пользователей",
    status_code=status.HTTP_200_OK,
    response_model=list[UserResponseSchema] # лист потому что вывод на несколько юзеров
    )
async def get_users():
    users = await users_crud.get_users()
    return users


@router.patch(
    "/users/{user_id}",
    tags=["Пользователи"],
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


@router.delete(
    "/users/{user_id}",
    tags=["Пользователи"],
    summary="Удалить пользователя",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(user_id: int):
    result = await users_crud.delete_user(
        user_id=user_id,
    )
    return result
