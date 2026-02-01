
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from src.api.dependencies import SessionDep
from src.models.todo_models import ListsORM, TasksORM, UsersORM
from src.schemas.todo_schemas import (
    TaskAddSchema,
    TaskPatchSchema,
    TaskResponseSchema,
    TaskUpdateSchema,
)

router = APIRouter()


@router.post(
    "/users/{id_user}/todo_lists/{id_list}/tasks",
    tags=["Задачи"],
    summary="Добавить задачи в лист задач по айди",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskResponseSchema,
    )
async def add_task(
    id_user: int,
    id_list: int,
    tsk: TaskAddSchema,
    session: SessionDep,
):
    query = select(ListsORM).where(
        ListsORM.user_id == id_user,
        ListsORM.id_list == id_list,
    )
    result = await session.execute(query)
    lst = result.scalar_one_or_none()
    if lst is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User or list not found"
            )

    new_tsk = TasksORM(
        task_name = tsk.task_name,
        completed = tsk.completed,
        list_id = id_list, # привязка по URL-идентификатору (если юзер не даст, возьмет из УРЛ)
    )

    session.add(new_tsk)
    await session.commit()
    await session.refresh(new_tsk)

    return new_tsk


@router.get(
    "/users/{id_user}/todo_lists/{id_list}/tasks",
    tags=["Задачи"],
    summary="Вывести все задачи",
    status_code=status.HTTP_200_OK,
    response_model=list[TaskResponseSchema],
    )
async def get_all_tasks(
    id_user: int,
    id_list: int,
    session: SessionDep
):
    query = (
        select(TasksORM)
        .join(ListsORM) # джоин для проверки и юзера и листа, тк юзера нет в тасках
        .where(
            TasksORM.list_id == id_list,
            ListsORM.user_id == id_user)
    )

    result = await session.execute(query)
    tsks = result.scalars().all()

    return tsks


# @router.put(
#     "/users/todo_lists/{id_task}",
#     tags=["Задачи"],
#     summary="Обновить все данные задачи",
#     status_code=status.HTTP_200_OK,
#     response_model=TaskResponseSchema,
#     )
# async def update_task(
#     id_task_to_update: int,
#     data: TaskUpdateSchema,
#     session: SessionDep,
# ):
#     query = select(TasksORM).where(TasksORM.id_task == id_task_to_update)
#     result = await session.execute(query)
#     tsk = result.scalar_one_or_none

#     if tsk is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

#     data_dict = data.model_dump()
#     for field_name, new_value in data_dict.items():
#         setattr(tsk, field_name, new_value)

#     await session.commit()
#     await session.refresh(tsk)

#     return tsk


@router.patch(
    "/users/{id_user}/todo_lists/{id_list}/{id_task}",
    tags=["Задачи"],
    summary="Обновить часть данных задачи",
    status_code=status.HTTP_200_OK,
    response_model=TaskResponseSchema,
    )
async def patch_task(
    id_task: int,
    id_user: int,
    id_list: int,
    data: TaskPatchSchema,
    session: SessionDep,
):
    query = (
        select(TasksORM)
        .join(ListsORM)
        .where(
            TasksORM.id_task == id_task,
            ListsORM.id_list == id_list,
            ListsORM.user_id == id_user)
    )
    result = await session.execute(query)
    tsk = result.scalar_one_or_none()

    if tsk is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    data_dict = data.model_dump(exclude_unset=True) # исключение неуказанных данных
    for field_name, new_value in data_dict.items():
        setattr(tsk, field_name, new_value)

    await session.commit()
    await session.refresh(tsk)

    return tsk


@router.delete(
    "/users/{id_user}/todo_lists/{id_list}/{id_task}",
    tags=["Задачи"],
    summary="Удалить задачу по айди",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    id_task: int,
    id_user: int,
    id_list: int,
    session: SessionDep
):
    query = (
        select(TasksORM)
        .join(ListsORM)
        .where(
            TasksORM.id_task == id_task,
            ListsORM.id_list == id_list,
            ListsORM.user_id == id_user)
    )
    result = await session.execute(query)
    tsk = result.scalar_one_or_none()

    if tsk is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    await session.delete(tsk)
    await session.commit()

    return None

# get по юзер айди для показа данных одного пользователя
# работа с листами и задачи должна идти по пользователю те по айди каждого, для get+post
# возврат модели юзера из пайдентика при удачном выполнении функции.
# коды ответа: 201 - пост, 204 - делит вместо по умолчанию 200. - DONE

# сделать отдельный репозиторий под проект апи
# перенести несделанные задачи в проект в репозитории

# вынести функции в отельный модуль (например db), переместить туда сами функции, сделать отдельный модуль с ручками
# и прописать в ручках вызов функций необходимых

# нейминг переменных в ручках
# переехать на постгресс
# авторизация
# депендс разобрать
# звернуть в докер с конфигов в файле
