from typing import Annotated

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.config import Base

intpk = Annotated[int, mapped_column(primary_key=True)]  # переменная для всех PK


class UsersORM(Base):
    __tablename__ = "users"

    id_user: Mapped[intpk]  # тип столбца через алиас-переменную
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(32))  # валидация длины

    # уникальность емейла удалена и использована в миграции бд
    email: Mapped[str | None] = mapped_column(String(64), nullable=True)
    hashed_password: Mapped[bytes] = mapped_column(
        nullable=False
    )  # поле для хранения хеша пароля

    # связь: один пользователь -> много списков (поэтому принимает список)
    user_lists: Mapped[list["ListsORM"]] = relationship(
        back_populates="user"
    )  # НЕ КОЛОНКА, А СВЯЗЬ!


class ListsORM(Base):
    __tablename__ = "lists"

    id_list: Mapped[intpk]
    title: Mapped[str]
    description: Mapped[str] = mapped_column(String(256))

    # столбец, который связан с таблицей пользователей по айди
    # также защищает от вставки несуществующего айди юзера
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id_user", ondelete="CASCADE")
    )

    # обратная связь список -> пользователь
    user: Mapped["UsersORM"] = relationship(
        back_populates="user_lists"
    )  # НЕ КОЛОНКА, А ОБРАТНАЯ СВЯЗЬ!

    # связь (НЕ КОЛОНКА): один лист -> много задач (поэтому принимает список)
    all_tasks: Mapped[list["TasksORM"]] = relationship(back_populates="todo_list")


class TasksORM(Base):
    __tablename__ = "tasks"

    id_task: Mapped[intpk]
    task_name: Mapped[str] = mapped_column(String(64))

    # нужен дефолт, иначе база будет требовать при каждом сохранении, если не передать.
    completed: Mapped[bool] = mapped_column(default=False)

    # столбец для хранение айди листа, связан как внешний ключ с таблицей листов
    # также защищает от вставки несуществующего айди листа с помощью ForeignKey
    list_id: Mapped[int] = mapped_column(
        ForeignKey("lists.id_list", ondelete="CASCADE")
    )

    # обратная связь много задач -> один лист
    todo_list: Mapped["ListsORM"] = relationship(back_populates="all_tasks")
