from sqlalchemy import select
from src.database.config import session_factory
from src.database.tables import UsersORM


async def get_user_by_email(email: str) -> UsersORM | None:
    """
    Проверить наличие юзера по мейлу в базе.
    """
    async with session_factory() as session:
        query = select(UsersORM).where(UsersORM.email == email)
        result = await session.execute(query)
        user = result.scalar_one_or_none() # проверка почты на уникальность в БД

        return user

async def create_user(name: str, email: str, hashed_password: bytes) -> UsersORM:
    """
    Создать пользователя с записью полей в базу.
    """
    async with session_factory() as session:
        new_user = UsersORM(
            name=name,
            email=email,
            hashed_password=hashed_password,
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user
