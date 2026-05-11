
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select

from src.auth.dependencies import get_user_status_by_token
from src.auth.schemas import UserReadSchema
from src.database.crud import todo_lists

# from src.api.dependencies import SessionDep
from src.database.crud import todo_lists as todo_lists_crud
from src.models.schemas import (
    ListAddSchema,
    ListPatchSchema,
    ListResponseSchema,
    ListUpdateSchema,
)

router = APIRouter(prefix="/me", tags=["Работа с листами задач"])

# ссылкается на схему в которой обязательно надо указывать айди юзера
# надо исправить схему или добавить отдельную
@router.post(
    "/to-do-lists",
    # tags=["Листы задач"],
    summary="Добавить лист задач",
    status_code=status.HTTP_201_CREATED,
    response_model=ListResponseSchema,
)
async def post_my_new_list(
    lst: ListAddSchema,
    user: UserReadSchema = Depends(get_user_status_by_token),
):
    id = user.id_user
    new_lst = await todo_lists.add_todo_lists(
        id_user=id,
        lst=lst,
    )
    if new_lst is None: # существование пользователя
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            )
    return new_lst


@router.get(
    "/to-do-lists",
    # tags=["Листы задач"],
    summary="Получить список своих листов задач",
    status_code=status.HTTP_200_OK,
    response_model=list[ListResponseSchema],
)
async def get_my_all_lists(
    user: UserReadSchema = Depends(get_user_status_by_token),
):
    result = await todo_lists.get_lists(
        id_user=user.id_user,
    )
    return result


@router.patch(
    "/to-do-lists/{list_id}",
    # tags=["Листы задач"],
    summary="Редактировать лист задач",
    status_code=status.HTTP_200_OK,
    response_model=ListResponseSchema,
)
async def edit_list(
    data: ListPatchSchema,
    list_id: int,
    user: UserReadSchema = Depends(get_user_status_by_token)
):
    edited_lst = await todo_lists_crud.patch_list(
        id_user=user.id_user,
        id_list=list_id,
        data=data
    )
    if edited_lst is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List or user not found"
        )
    return edited_lst

@router.delete(
    "/to-do-lists/{list_id}",
    # tags=["Листы задач"],
    summary="Удалить лист задач",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_list(
    list_id: int,
    user: UserReadSchema = Depends(get_user_status_by_token),
):
    deleted_list = await todo_lists_crud.delete_list(
        id_user=user.id_user,
        id_list=list_id
    )
    if deleted_list is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List or user not found")

    return None


# админские роуты
admin = APIRouter(tags=["Admin"])


@admin.post(
    "/users/{id_user}/todo_lists", # доступ к листу по идентификатору пользователя
    tags=["Admin"],
    summary="Добавить лист задач для указанного пользователя",
    status_code=status.HTTP_201_CREATED,
    response_model=ListResponseSchema,
    )
async def add_list(
    id_user: int,
    lst: ListAddSchema,
):
    new_lst = await todo_lists_crud.add_todo_lists(
        id_user=id_user,
        lst=lst,
    )
    return new_lst

@admin.get(
    "/users/{id_user}/todo_lists",
    tags=["Admin"],
    summary="Показать все листы задач указанного пользователя",
    status_code=status.HTTP_200_OK,
    response_model=list[ListResponseSchema], # вернуть список схем, тк листов несколько
)
async def get_lists(id_user: int):
    result = await todo_lists_crud.get_lists(
        id_user=id_user,
    )
    return result

@admin.patch(
    "/users/{id_user}/todo_lists/{id_list}",
    tags=["Admin"],
    summary="Обновить часть данных листа задач",
    status_code=status.HTTP_200_OK,
    response_model=ListResponseSchema,
)
async def edit(
    id_user: int,
    id_list: int,
    data: ListPatchSchema,
):
    edited_lst = await todo_lists_crud.patch_list(
        id_user=id_user,
        id_list=id_list,
        data=data,
    )
    return edited_lst

@admin.delete(
    "/users/{id_user}/todo_lists/{id_list}",
    tags=["Admin"],
    summary="Удалить лист задач",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_lst(
    id_user: int,
    id_list: int,
):
    await todo_lists_crud.delete_list(
        id_user=id_user,
        id_list=id_list,
    )
    return None
