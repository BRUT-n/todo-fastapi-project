from typing import Annotated

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base

intpk = Annotated[int, mapped_column(primary_key=True)] # переменная для всех PK

class UsersORM(Base):
    __tablename__ = "users"

    id_user: Mapped[intpk] # тип столбца через алиас-переменную
    name: Mapped[str] = mapped_column(String(32)) # валидация длины
    email:Mapped[str] = mapped_column(String(32), unique=True, nullable=False) # уникальность емейла
    # email: Mapped[str | None] = mapped_column(String(32), nullable=True) #EmailStr | None # валидация эмейла или пусто - НЕВЕРНО, ВАЛИДАЦИЯ ЧЕРЕЗ ПАЙДЕНТИК ТОЛЬКО В СХЕМАХ АПИ

    user_lists: Mapped[list["ListsORM"]] = relationship(back_populates="user") # НЕ КОЛОНКА, А СВЯЗЬ!
    # связь: один пользователь -> много списков (поэтому принимает список)

    # model_config = ConfigDict(extra="forbid") запрет на лишние данные - не работает в алхимии, только в пайдентик

class ListsORM(Base):
    __tablename__ = "lists"

    id_list: Mapped[intpk]
    title: Mapped[str]
    description: Mapped[str] = mapped_column(String(256))

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id_user", ondelete="CASCADE"))
    # столбец, который связан с таблицей пользователей по айди
    # также защищает от вставки несуществующего айди юзера

    user: Mapped["UsersORM"] = relationship(back_populates="user_lists") # НЕ КОЛОНКА, А ОБРАТНАЯ СВЯЗЬ!
    # обратная связь список -> пользователь

    all_tasks: Mapped[list["TasksORM"]] = relationship(back_populates="todo_list")
    # связь (НЕ КОЛОНКА): один лист -> много задач (поэтому принимает список)

class TasksORM(Base):
    __tablename__ = "tasks"

    id_task: Mapped[intpk]
    task_name: Mapped[str] = mapped_column(String(64))
    completed: Mapped[bool] = mapped_column(default=False) # добавлен дефолт иначе база будет требовать её при каждом сохранении, если вы забудете её передать.

    list_id: Mapped[int] = mapped_column(ForeignKey("lists.id_list", ondelete="CASCADE"))
    # столбец для хранение айди листа, связан как внешний ключ с таблицей листов
    # также защищает от вставки несуществующего айди листа с помощью ForeignKey

    todo_list: Mapped["ListsORM"] = relationship(back_populates="all_tasks")
    # обратная связь много задач -> один лист
