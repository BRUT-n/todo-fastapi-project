from fastapi import APIRouter
from sqlalchemy import delete, select
from src.database.config import session_factory
from src.database.tables import UsersORM
from src.models.schemas import (
    UserPatchSchema,
)

router = APIRouter()


async def patch_user(
    user_id: int,
    data: UserPatchSchema,
) -> UsersORM | None:
    """
    Обновляет часть сущности.
    Требует передать поля, которые надо поменять у объекта.
    Частично заменяет старые данные, только те, что переданы в функцию.
    """
    async with session_factory() as session:
        query = select(UsersORM).where(
            UsersORM.id_user == user_id
        )  # запрос на получение данных
        result = await session.execute(query)  # выполнение запроса асинхронно
        user = (
            result.scalar_one_or_none()
        )  # распаковка полученного кортежа в один объект

        if user is None:
            return None  # обрабатывается в роуте

        # превращает !только переданные данные! Pydantic-модели в словарь
        data_dict = data.model_dump(exclude_unset=True)

        for (
            field_name,
            new_value,
        ) in data_dict.items():  # итерация по данным которые были указаны
            setattr(
                user, field_name, new_value
            )  # спец функция на замену данных по типу user.name = "Ivan".

        await session.commit()
        await session.refresh(user)  # обновление по новым записанным данным

        return user


async def delete_user(
    user_id: int,
) -> None:
    async with session_factory() as session:
        query = (
            delete(UsersORM).where(UsersORM.id_user == user_id)
            # .returning(UsersORM.id_user) # возврат удаленного айди
        )  # прямой запрос на удаление пользователя
        await session.execute(query)

        await session.commit()
        return None
