from collections.abc import Sequence

from fastapi import APIRouter
from sqlalchemy import delete, select
from src.database.config import session_factory
from src.database.tables import ListsORM
from src.models.schemas import (
    ListAddSchema,
    ListPatchSchema,
)

router = APIRouter()


async def add_todo_lists(
    id_user: int,
    lst: ListAddSchema,
) -> None | ListsORM:
    """
    Передавать в id_user только id существующего в базе пользователя.
    """
    async with session_factory() as session:
        new_lst = ListsORM(
            title=lst.title,
            description=lst.description,
            user_id=id_user,  # привязка по URL-идентификатору
        )

        session.add(new_lst)
        await session.commit()
        await session.refresh(new_lst)

        return new_lst


async def get_lists(
    id_user: int,
    limit: int = 5,
    offset: int = 0,
) -> Sequence[ListsORM]:
    async with session_factory() as session:
        query = (
            select(ListsORM)
            .where(ListsORM.user_id == id_user)
            .order_by(ListsORM.id_list)  # сортировка для предсказуемости вывода
            .limit(limit)  # лимит вывода строк
            .offset(
                offset
            )  # смещение - сколько пропускать строк считая от первой строки
        )
        result = await session.execute(query)
        lists = (
            result.scalars().all()
        )  # достаем список ORM-объектов в виде списка пайтон-объектов
        return lists  # преобразует ORM → Pydantic


async def patch_list(
    id_user: int,
    id_list: int,
    data: ListPatchSchema,
) -> ListsORM | None:
    async with session_factory() as session:
        query = select(ListsORM).where(
            ListsORM.id_list == id_list,
            ListsORM.user_id == id_user,
        )
        result = await session.execute(query)
        lst = result.scalar_one_or_none()

        if lst is None:
            return None

        data_dict = data.model_dump(
            exclude_unset=True
        )  # создать словарь на основе схемы исключая не переданные поля
        for field_name, new_value in data_dict.items():
            setattr(lst, field_name, new_value)

        await session.commit()
        await session.refresh(lst)

        return lst


async def delete_list(
    id_user: int,
    id_list: int,
):
    async with session_factory() as session:
        query = (
            delete(ListsORM)
            .where(ListsORM.id_list == id_list, ListsORM.user_id == id_user)
            .returning(ListsORM.id_list)
        )
        result = await session.execute(query)
        deleted_id_list = result.scalar_one_or_none()

        if deleted_id_list is None:
            return False

        await session.commit()

        return True
