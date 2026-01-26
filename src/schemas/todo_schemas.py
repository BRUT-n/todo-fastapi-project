from pydantic import BaseModel, ConfigDict, EmailStr, Field


# валидация данных pydentic при создании
class UserAddSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=32) # валидация длины перед отправкой в БД!
    email: EmailStr
    # email: EmailStr | None = None # по умолчанию устанавливать None, или надо писать в вводе null, чтобы проходила валидация
    model_config = ConfigDict(extra="forbid") # запрет на лишние данные работает только в пайдентик


class ListAddSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=32) #  (...) называются Ellipsis, означают, что поле является обязательным
    description: str = Field(..., min_length=1, max_length=256)
    user_id: int = Field(..., ge=1) # запрещает 0

class TaskAddSchema(BaseModel):
    task_name: str = Field(..., min_length=4, max_length=64)
    completed: bool = Field(default=False)
    list_id: int = Field(..., ge=1) # запрещает 0

# схемы для обновления данных
class UserUpdateSchema(UserAddSchema): # полная замена данных
    """
    перенаследование от схемы добавление
    тк код и поля не меняется
    """
    pass

class UserPatchSchema(BaseModel): # частичная замена данных
    """
    перенаследование от базы, потому что
    переопределение с обязательной на необязательную не круто
    """
    name: str | None = Field(None, min_length=2, max_length=32)
    email: EmailStr | None = None
    model_config = ConfigDict(extra="forbid")

class ListUpdateSchema(ListAddSchema):
    pass

class ListPatchSchema(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=32) #  (...) называются Ellipsis, означают, что поле является обязательным
    description: str | None = Field(None, min_length=1, max_length=256)
    user_id: int | None = Field(None, ge=1) # запрещает 0

class TaskUpdateSchema(TaskAddSchema):
    pass

class TaskPatchSchema(BaseModel):
    task_name: str | None = Field(None, min_length=4, max_length=64)
    completed: bool | None = Field(None)
    # По умолчанию None. Если в JSON поля нет — будет None. А model_dump(exclude_unset=True) не возьмет Ноне в словарь
    list_id: int | None = Field(None, ge=1) # запрещает 0

# схемы для ответа
class UserResponseSchema(BaseModel):
    id_user: int
    name: str
    email: str | None

    model_config=ConfigDict(from_attributes=True)

class ListResponseSchema(BaseModel):
    id_list: int
    title: str
    description: str | None
    user_id: int

    # Позволяет Pydantic работать с объектами SQLAlchemy, пытаясь прочитать атрибуты и сделать себе словарь
    # Для каждого поля в схеме (например, id, name) он делает: getattr(db_user, "id"), getattr(db_user, "name").
    model_config=ConfigDict(from_attributes=True)

class TaskResponseSchema(BaseModel):
    id_task: int
    task_name: str
    completed: bool
    list_id: int

    model_config=ConfigDict(from_attributes=True)
