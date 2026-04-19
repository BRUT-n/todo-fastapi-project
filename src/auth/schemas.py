from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserRegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

# дом. фильтр - то что возвращается юзеру (никаких чувствительных данных)
class UserReadSchema(BaseModel):
    model_config = ConfigDict(strict=True)
    id_user: int
    name: str
    email: EmailStr

# по стандарту OAuth2 структура ответа при выдаче токена
class TokenInfo(BaseModel):
    access_token: str
    token_type: str = "Bearer"

class TokenPayload(BaseModel):
    sub: str
    iat: int
    exp: int

# модель для авторизации
class UserAuthSchema(BaseModel):
    model_config = ConfigDict(strict=True) # Строго ограничение, чтобы не принимал иные данные и не пытался их привести в нужные

    # name: str
    email: EmailStr
    password: bytes # обычно в виде строки, но это реализовано дополнительно в коде
    # active: bool = True
