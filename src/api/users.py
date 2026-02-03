from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, delete
from src.api.dependencies import SessionDep
from src.database import Base, engine
from src.models.todo_models import UsersORM
from src.schemas.todo_schemas import (
    UserAddSchema,
    UserPatchSchema,
    UserResponseSchema,
    UserUpdateSchema,
)
from src.crud.users import add_user as add_user_crud
from src.crud.users import get_users as get_user_crud
from src.crud.users import patch_user as patch_user_crud
from src.crud.users import delete_user as delete_user_crud


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
async def create_user(user_in: UserAddSchema, session: SessionDep):
    new_user = await add_user_crud(user=user_in, session=session)
    return new_user


@router.get(
    "/users",
    tags=["Пользователи"],
    summary="Вывести всех пользователей",
    status_code=status.HTTP_200_OK,
    response_model=list[UserResponseSchema] # лист потому что вывод на несколько юзеров
    )
async def get_users(session: SessionDep):
    users = await get_user_crud(session=session)
    return users

@router.patch(
    "/users/{user_id}",
    tags=["Пользователи"],
    summary="Обновить часть данных пользователя",
    status_code=status.HTTP_200_OK,
    response_model=UserResponseSchema,
) # заменяет указанные свойства
async def patch_user(user_id: int, data: UserPatchSchema, session: SessionDep):
    patched_user = await patch_user_crud(user_id=user_id, data=data, session=session)
    return patched_user

@router.delete(
    "/users/{user_id}",
    tags=["Пользователи"],
    summary="Удалить пользователя",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(user_id: int, session: SessionDep):
    result = await delete_user_crud(user_id=user_id, session=session)
    return result

