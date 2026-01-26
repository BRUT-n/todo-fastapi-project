from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, delete
from src.api.dependencies import SessionDep
from src.database import Base, engine
from src.models.todo_models import UsersORM
from src.schemas.todo_schemas import (
    UserAddSchema,
    UserPatchSchema,
    UserResponseSchema,
    UserUpdateSchema,
)

router = APIRouter()

# @router.post(
#     "/database",
#     tags=["Взаимодейсвие с БД"]
#     ) # в лайфспан
# async def setup_database():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#     return {"ok": True, "message" : "Database droped and created again"}


@router.post(
    "/users", tags=["Пользователи"],
    summary="Добавление пользователя",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseSchema,
    )
async def add_user(
    user: UserAddSchema,
    session: SessionDep
):
    query = (
        select(UsersORM)
        .where(UsersORM.email == user.email) # проверка мейла из базы и переданного на уникальность
    )
    result = await session.execute(query)
    existing_mail = result.scalar_one_or_none()

    if existing_mail:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # ошибка конфликта на сервере
            detail="Email already registered")

    new_user = UsersORM(
        name=user.name, # данные name модели ОРМ берутся из схемы переданой в аргумент
        email=user.email,
    )

    session.add(new_user) # await не надо, потому что нет обращения к БД
    await session.commit()
    await session.refresh(new_user) # обновляет данные в памяти, чтобы вернуть то что база заполнила сама

    return new_user
    # {"ok": True,
    #         "message": "User added",
    #         "user_id": new_user.id_user} # выдает присвоенный айди юзера, работает только с refresh

"""
Проблема асинхронности (ошибка greenlet)
await session.refresh(new_user) делает микрозапрос на обновление данных вытягивая из БД
нужен для возврата созданного ID или любые поля, которые заполняет база
"""

@router.get(
    "/users",
    tags=["Пользователи"],
    summary="Вывести всех пользователей",
    status_code=status.HTTP_200_OK,
    response_model=list[UserResponseSchema] # лист потому что вывод на несколько юзеров
    )
async def get_users(session: SessionDep):
    query = select(UsersORM)
    result = await session.execute(query)

    users = result.scalars().all() # scalars() распаковывает кортежи для удобства чтения и доступа через срезы
    return users

# @router.put("/users/{user_id}", tags=["Пользователи"], summary="Обновить все данные пользователя", status_code=status.HTTP_200_OK) # заменяет все свойства
# async def update_user(user_id_for_update: int, data: UserUpdateSchema, session: SessionDep):
#     """
#     Обновляет всю сущность целиком.
#     Требует передать все поля, которые есть у объекта.
#     Обычно приводит объект в «желаемое состояние», полностью заменяя старые данные новыми.
#     """
#     query = select(UsersORM).where(UsersORM.id_user == user_id_for_update) # запрос на получение данных
#     result = await session.execute(query) # выполнение запроса асинхронно
#     user = result.scalar_one_or_none() # распаковка полученного кортежа в один объект
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found") # ошибка 404 если запрос вернул ничего

#     data_dict = data.model_dump() # превращает все данные Pydantic-модели (входящие данные) в словарь
#     for field_name, new_value in data_dict.items(): # итерация по данным которые будут вписаны
#         setattr(user, field_name, new_value) # спец функция на замену данных по типу user.name = "Ivan".

#     await session.commit()
#     # await session.refresh(user) # обновление по новым записанным данным
#     return {"ok": True, "message": f"User with id {user_id_for_update} updated"}

@router.patch(
    "/users/{user_id_for_patch}",
    tags=["Пользователи"],
    summary="Обновить часть данных пользователя",
    status_code=status.HTTP_200_OK,
    response_model=UserResponseSchema,
) # заменяет указанные свойства
async def patch_user(
    user_id_for_patch: int,
    data: UserPatchSchema,
    session: SessionDep):
    """
    Обновляет часть сущности.
    Требует передать поля, которые надо поменять у объекта.
    Частично заменяет старые данные, только те, что переданы в функцию.
    """
    query = (
        select(UsersORM)
        .where(UsersORM.id_user == user_id_for_patch)
    ) # запрос на получение данных
    result = await session.execute(query) # выполнение запроса асинхронно
    user = result.scalar_one_or_none() # распаковка полученного кортежа в один объект

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found") # ошибка 404 если запрос вернул ничего

    data_dict = data.model_dump(exclude_unset=True) # превращает !только переданные данные! Pydantic-модели в словарь

    new_email = data_dict.get("email") # проверка на вход - меняют емейл?
    if new_email and new_email != user.email: # проверка полученного и того, что в БД(user.email)
        query_check = (
            select(UsersORM)
            .where(UsersORM.email == new_email) # проверка мейла из базы и переданного на уникальность
        )
        result_check = await session.execute(query_check)
        existing_mail = result_check.scalar_one_or_none() # либо да либо Ноне

        if existing_mail:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, # ошибка конфликта на сервере
                detail="Email already registered")

    for field_name, new_value in data_dict.items(): # итерация по данным которые были указаны
        setattr(user, field_name, new_value) # спец функция на замену данных по типу user.name = "Ivan".

    await session.commit()
    await session.refresh(user) # обновление по новым записанным данным

    return user

@router.delete(
    "/users/{user_id_for_delete}",
    tags=["Пользователи"],
    summary="Удалить пользователя",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(user_id_for_delete: int, session: SessionDep):
    # query = (
    #     select(UsersORM)
    #     .where(UsersORM.id_user == user_id_for_delete)
    # )

    # result = await session.execute(query)
    # user = result.scalar_one_or_none()
    # if user is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="User not found") # ошибка 404 если запрос вернул ничего
    # await session.delete(user)

    query = (
        delete(UsersORM)
        .where(UsersORM.id_user == user_id_for_delete)
        .returning(UsersORM.id_user)
    ) # прямой запрос на удаление пользователя

    result = await session.execute(query)
    deleted_user_id = result.scalar_one_or_none() # проверка - вернулся ли удаленный айди?

    if deleted_user_id is None: # если айди не вернулся, значит пользователя нет и удаления не выполнено
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found") # ошибка 404 если запрос вернул ничего

    await session.commit()
    return None


