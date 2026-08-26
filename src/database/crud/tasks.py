from typing import Sequence

from fastapi import APIRouter
from sqlalchemy import select
from src.database.config import session_factory
from src.database.tables import ListsORM, TasksORM
from src.models.schemas import (
    TaskAddSchema,
    TaskPatchSchema,
)

router = APIRouter()


async def add_task(
    id_user: int,
    id_list: int,
    tsk: TaskAddSchema,
) -> None | TasksORM:
    async with session_factory() as session:
        query = select(ListsORM).where(
            ListsORM.user_id == id_user,
            ListsORM.id_list == id_list,
        )
        result = await session.execute(query)
        lst = result.scalar_one_or_none()
        if lst is None:
            return None

        # можно сделать распаковкой и через model_dump
        # new_tsk = TasksORM(
        # **tsk.model_dump(),
        # list_id=id_list
        # )
        new_tsk = TasksORM(
            task_name = tsk.task_name,
            completed = tsk.completed,
            list_id = id_list, # привязка по URL-идентификатору (если юзер не даст, возьмет из УРЛ)
        )

        session.add(new_tsk)
        await session.commit()
        await session.refresh(new_tsk)

        return new_tsk


async def get_all_tasks(
    id_user: int,
    id_list: int,
    limit: int = 5,
    offset: int = 0,
) -> Sequence[TasksORM]:
    async with session_factory() as session:
        query = (
            select(TasksORM)
            .join(ListsORM) # джоин для проверки и юзера и листа, тк юзера_айди нет в тасках
            .where(
                TasksORM.list_id == id_list,
                ListsORM.user_id == id_user
            )
            .order_by(TasksORM.id_task) # сортировка для предсказуемости вывода
            .limit(limit) # лимит вывода строк
            .offset(offset) # смещение - сколько пропускать строк считая от первой строки
        )

        result = await session.execute(query)
        tsks = result.scalars().all()

        return tsks


async def patch_task(
    id_task: int,
    id_user: int,
    id_list: int,
    data: TaskPatchSchema,
) -> None | TasksORM:
    async with session_factory() as session:
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
            return None

        data_dict = data.model_dump(exclude_unset=True) # исключение неуказанных данных
        for field_name, new_value in data_dict.items():
            setattr(tsk, field_name, new_value)

        await session.commit()
        await session.refresh(tsk)

        return tsk


async def delete_task(
    id_task: int,
    id_user: int,
    id_list: int,
):
    async with session_factory() as session:
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
            return False

        await session.delete(tsk)
        await session.commit()

        return True
