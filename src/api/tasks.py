
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# from src.api.dependencies import SessionDep
from src.auth.dependencies import get_user_status_by_token
from src.auth.schemas import UserReadSchema
from src.database.crud import tasks as tasks_crud
from src.models.schemas import (
    TaskAddSchema,
    TaskPatchSchema,
    TaskResponseSchema,
    TaskUpdateSchema,
)

router = APIRouter(prefix="/me", tags=["Работа с задачами внутри списков"])


@router.post(
    "/todo_lists/{id_list}/tasks",
    summary="Добавить задачу в лист по айди",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskResponseSchema,
    )
async def create_task_in_lst(
    id_list:int,
    task: TaskAddSchema,
    user: UserReadSchema = Depends(get_user_status_by_token),
):
    new_tsk = await tasks_crud.add_task(
        id_user=user.id_user,
        id_list=id_list,
        tsk=task,
    )
    return new_tsk

@router.get(
    "/todo_lists/{id_list}/tasks",
    summary="Вывести все задачи",
    status_code=status.HTTP_200_OK,
    response_model=list[TaskResponseSchema],
    )
async def get_tasks_from_list(
    id_list: int,
    user: UserReadSchema = Depends(get_user_status_by_token),
):
    result = await tasks_crud.get_all_tasks(
        id_user=user.id_user,
        id_list=id_list,
    )
    return result

@router.patch(
    "/todo_lists/{id_list}/tasks/{id_task}",
    summary="Обновить часть данных задачи",
    status_code=status.HTTP_200_OK,
    response_model=TaskResponseSchema,
    )
async def edit_task_in_lst(
    id_task: int,
    id_list: int,
    data: TaskPatchSchema,
    user: UserReadSchema= Depends(get_user_status_by_token)
):
    edited_task = await tasks_crud.patch_task(
        id_task=id_task,
        id_user=user.id_user,
        id_list=id_list,
        data=data,
    )
    return edited_task

@router.delete(
    "/todo_lists/{id_list}/tasks/{id_task}",
    summary="Удалить задачу по айди",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_from_lst(
    id_task: int,
    id_list: int,
    user: UserReadSchema = Depends(get_user_status_by_token)
):
    await tasks_crud.delete_task(
        id_task=id_task,
        id_user=user.id_user,
        id_list=id_list,
    )
    return None


# админские роуты
admin = APIRouter()

@admin.post(
    "/users/{id_user}/todo_lists/{id_list}/tasks",
    tags=["Admin"],
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

@admin.get(
    "/users/{id_user}/todo_lists/{id_list}/tasks",
    tags=["Admin"],
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

@admin.patch(
    "/users/{id_user}/todo_lists/{id_list}/{id_task}",
    tags=["Admin"],
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

@admin.delete(
    "/users/{id_user}/todo_lists/{id_list}/{id_task}",
    tags=["Admin"],
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