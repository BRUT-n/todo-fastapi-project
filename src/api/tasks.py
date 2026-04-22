
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import TableSample, select
from sqlalchemy.ext.asyncio import AsyncSession

# from src.api.dependencies import SessionDep
from src.database.crud import tasks as tasks_crud
from src.database.tables import ListsORM, TasksORM, UsersORM
from src.models.schemas import (
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
    id_list:int,
    task: TaskAddSchema,
):
    new_tsk = await tasks_crud.add_task(
        id_user=id_user,
        id_list=id_list,
        tsk=task,
    )
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
):
    result = await tasks_crud.get_all_tasks(
        id_user=id_user,
        id_list=id_list,
    )
    return result


@router.patch(
    "/users/{id_user}/todo_lists/{id_list}/{id_task}",
    tags=["Задачи"],
    summary="Обновить часть данных задачи",
    status_code=status.HTTP_200_OK,
    response_model=TaskResponseSchema,
    )
async def edit_task(
    id_task: int,
    id_user: int,
    id_list: int,
    data: TaskPatchSchema,
):
    edited_task = await tasks_crud.patch_task(
        id_task=id_task,
        id_user=id_user,
        id_list=id_list,
        data=data,
    )
    return edited_task


@router.delete(
    "/users/{id_user}/todo_lists/{id_list}/{id_task}",
    tags=["Задачи"],
    summary="Удалить задачу по айди",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    id_task: int,
    id_user: int,
    id_list: int,
):
    await tasks_crud.delete_task(
        id_task=id_task,
        id_user=id_user,
        id_list=id_list,
    )
    return None
