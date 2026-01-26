
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import delete, select
from src.api.dependencies import SessionDep
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
async def add_todo_lists(
    id_user: int,
    lst: ListAddSchema,
    session: SessionDep
):
    user = await session.get(UsersORM, id_user)
    if user is None: # существование пользователя проеверяется
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            )

    new_lst = ListsORM(
        title=lst.title,
        description=lst.description,
        user_id=id_user # привязка по URL-идентификатору
    )

    session.add(new_lst)
    await session.commit()
    await session.refresh(new_lst)

    return new_lst

    # {
    #         "ok": True,
    #         "message": "To do list added",
    #         "todo_list_id": new_lst.id_list, # возвращает присвоенные айди из базы
    #         "Relationship with user_id": new_lst.user_id # возвращает присвоенные айди из ввода пользователя
    #     }


@router.get(
    "/users/{id_user}/todo_lists",
    tags=["Листы"],
    summary="Показать все листы задач указанного пользователя",
    status_code=status.HTTP_200_OK,
    response_model=list[ListResponseSchema], # вернуть список схем, тк листов несколько
)
async def get_lists(
    id_user: int,
    session: SessionDep,
):
    query = select(ListsORM).where(ListsORM.user_id == id_user)
    result = await session.execute(query)
    lists = result.scalars().all() # достаем список ORM-объектов
    return lists # преобразует ORM → Pydantic


# @router.put(
#     "/users/{id_user_of_list}/todo_lists/{id_list_for_update}",
#     tags=["Листы"],
#     summary="Обновить все данные указанного листа задач выбранного пользователя",
#     status_code=status.HTTP_200_OK,
#     response_model=ListResponseSchema, # схемы для ответа
# )
# async def update_list(
#     id_user_of_list: int,
#     id_list_for_update: int,
#     data: ListUpdateSchema,
#     session: SessionDep,
# ):
#     query = select(ListsORM).where(
#         ListsORM.user_id == id_user_of_list,
#         ListsORM.id_list == id_list_for_update,
#     )
#     result = await session.execute(query)
#     lst = result.scalar_one_or_none()

#     if lst is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="List not found",
#         )

#     data_dict = data.model_dump()
#     for field_name, new_value in data_dict.items():
#         setattr(lst, field_name, new_value)

#     await session.commit()
#     await session.refresh(lst) # вытаскивает данные из бд после комита

#     return lst


@router.patch(
    "/users/{id_user_of_list}/todo_lists/{id_list_for_patch}",
    tags=["Листы"],
    summary="Обновить часть данных листа задач",
    status_code=status.HTTP_200_OK,
    response_model=ListResponseSchema,
)
async def patch_list(
    id_user_of_list: int,
    id_list_for_patch: int,
    data: ListPatchSchema,
    session: SessionDep,
):
    query = select(ListsORM).where(
        ListsORM.id_list == id_list_for_patch,
        ListsORM.user_id == id_user_of_list,
    )
    result = await session.execute(query)
    lst = result.scalar_one_or_none()

    if lst is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List or user not found"
        )

    data_dict = data.model_dump(exclude_unset=True) # создать словарь на основе схемы исключая не переданные поля
    for field_name, new_value in data_dict.items():
        setattr(lst, field_name, new_value)

    await session.commit()
    await session.refresh(lst)

    return lst


@router.delete(
    "/users/{id_user_of_list}/todo_lists/{id_list_for_delete}",
    tags=["Листы"],
    summary="Удалить лист задач",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_list(
    id_user_of_list: int,
    id_list_for_delete: int,
    session:SessionDep,
):
    # query = select(ListsORM).where(
    #     ListsORM.id_list == id_list_for_delete,
    #     ListsORM.user_id == id_user_of_list,
    # )
    # result = await session.execute(query)
    # lst = result.scalar_one_or_none()

    # if lst is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="List or user not found")

    # await session.delete(lst)

    query = (
        delete(ListsORM)
        .where(
            ListsORM.id_list == id_list_for_delete,
            ListsORM.user_id == id_user_of_list)
        .returning(ListsORM.id_list)
    )
    result = await session.execute(query)
    deleted_id_list = result.scalar_one_or_none()

    if deleted_id_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List or user not found")

    await session.commit()

    return None

