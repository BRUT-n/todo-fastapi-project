from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.auth.dependencies import get_user_status_by_token
from src.auth.schemas import UserReadSchema
from src.database.crud import todo_lists
from src.database.crud import todo_lists as todo_lists_crud
from src.models.schemas import (
    ListAddSchema,
    ListPatchSchema,
    ListResponseSchema,
)

router = APIRouter(prefix="/me", tags=["Работа с листами задач"])


@router.post(
    "/to-do-lists",
    summary="Добавить лист задач",
    status_code=status.HTTP_201_CREATED,
    response_model=ListResponseSchema,
)
async def post_my_new_list(
    lst: ListAddSchema,
    user: UserReadSchema = Depends(get_user_status_by_token),
):
    new_lst = await todo_lists.add_todo_lists(
        id_user=user.id_user,
        lst=lst,
    )
    return new_lst


@router.get(
    "/to-do-lists",
    summary="Получить список своих листов задач",
    status_code=status.HTTP_200_OK,
    response_model=list[ListResponseSchema],
)
async def get_my_all_lists(
    limit: int = Query(
        default=5,
        ge=1,
        le=20,
        title="Лимит листов на вывод пользователю.",
        description=(
            "Количество списков задач, которое нужно вернуть"
            "на одной странице (размер страницы)."
        ),
    ),
    offset: int = Query(
        default=0,
        ge=0,
        title="Смещение (сдвиг) для перехода по страницам.",
        description="Количество списков, которое нужно пропустить от начала.",
    ),
    user: UserReadSchema = Depends(get_user_status_by_token),
):
    result = await todo_lists.get_lists(
        id_user=user.id_user,
        limit=limit,
        offset=offset,
    )
    return result


@router.patch(
    "/to-do-lists/{list_id}",
    summary="Редактировать лист задач",
    status_code=status.HTTP_200_OK,
    response_model=ListResponseSchema,
)
async def edit_list(
    data: ListPatchSchema,
    list_id: int,
    user: UserReadSchema = Depends(get_user_status_by_token),
):
    edited_lst = await todo_lists_crud.patch_list(
        id_user=user.id_user, id_list=list_id, data=data
    )
    if edited_lst is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="List not found"
        )
    return edited_lst


@router.delete(
    "/to-do-lists/{list_id}",
    summary="Удалить лист задач",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_list(
    list_id: int,
    user: UserReadSchema = Depends(get_user_status_by_token),
):
    deleted_list = await todo_lists_crud.delete_list(
        id_user=user.id_user, id_list=list_id
    )
    if deleted_list is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="List not found"
        )

    return None
