
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import delete, select

from src.api.dependencies import SessionDep
from src.crud import todo_lists as todo_lists_crud
from src.models.todo_models import ListsORM, UsersORM
from src.schemas.todo_schemas import (
    ListAddSchema,
    ListPatchSchema,
    ListResponseSchema,
    ListUpdateSchema,
)

router = APIRouter()


@router.post(
    "/users/{id_user}/todo_lists", # доступ к листу по идентификатору пользователя
    tags=["Листы"],
    summary="Добавить лист задач для указанного пользователя",
    status_code=status.HTTP_201_CREATED,
    response_model=ListResponseSchema,
    )
async def add_list(
    id_user: int,
    lst: ListAddSchema,
    session: SessionDep
):
    new_lst = await todo_lists_crud.add_todo_lists(
        id_user=id_user,
        lst=lst,
        session=session
    )
    return new_lst


@router.get(
    "/users/{id_user}/todo_lists",
    tags=["Листы"],
    summary="Показать все листы задач указанного пользователя",
    status_code=status.HTTP_200_OK,
    response_model=list[ListResponseSchema], # вернуть список схем, тк листов несколько
)
async def get_lists(id_user: int, session: SessionDep):
    result = await todo_lists_crud.get_lists(
        id_user=id_user,
        session=session
    )
    return result


@router.patch(
    "/users/{id_user}/todo_lists/{id_list}",
    tags=["Листы"],
    summary="Обновить часть данных листа задач",
    status_code=status.HTTP_200_OK,
    response_model=ListResponseSchema,
)
async def edit_list(
    id_user: int,
    id_list: int,
    data: ListPatchSchema,
    session: SessionDep
):
    edited_lst = await todo_lists_crud.patch_list(
        id_user=id_user,
        id_list=id_list,
        data=data,
        session=session
    )
    return edited_lst


@router.delete(
    "/users/{id_user}/todo_lists/{id_list}",
    tags=["Листы"],
    summary="Удалить лист задач",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_lst(
    id_user: int,
    id_list: int,
    session: SessionDep
):
    await todo_lists_crud.delete_list(
        id_user=id_user,
        id_list=id_list,
        session=session
    )
    return None
