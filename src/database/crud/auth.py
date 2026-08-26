from sqlalchemy import select
from src.database.config import session_factory
from src.database.tables import UsersORM


async def get_user_by_username(username: str) -> UsersORM | None:
    """
    Проверить наличие юзера по username в базе.
    """
    async with session_factory() as session:
        query = select(UsersORM).where(UsersORM.username == username)
        result = await session.execute(query)
        user = result.scalar_one_or_none() # проверка username на уникальность в БД

        return user


async def get_user_by_id(user_id: int) -> UsersORM | None:
    """
    Получить пользователя по его уникальному ID
    """
    async with session_factory() as session:
        query = select(UsersORM).where(UsersORM.id_user == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        return user


async def create_user(username: str, name: str, hashed_password: bytes, email: str | None = None, ) -> UsersORM:
    """
    Создать пользователя с записью полей в базу.
    """
    async with session_factory() as session:
        new_user = UsersORM(
            username=username,
            name=name,
            email=email,
            hashed_password=hashed_password,
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user
