
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import TableSample, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import SessionDep
from src.crud import tasks as tasks_crud
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
    id_list:int,
    task: TaskAddSchema,
    session: SessionDep
):
    new_tsk = await tasks_crud.add_task(
        id_user=id_user,
        id_list=id_list,
        tsk=task,
        session=session
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
    session:SessionDep
):
    result = await tasks_crud.get_all_tasks(
        id_user=id_user,
        id_list=id_list,
        session=session
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
    session: SessionDep
):
    edited_task = await tasks_crud.patch_task(
        id_task=id_task,
        id_user=id_user,
        id_list=id_list,
        data=data,
        session=session
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
    session: SessionDep
):
    await tasks_crud.delete_task(
        id_task=id_task,
        id_user=id_user,
        id_list=id_list,
        session=session
    )
    return None
