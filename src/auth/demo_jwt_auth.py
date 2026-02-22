from fastapi import (  # для формы нужен python-multipart
    APIRouter,
    Depends,
    Form,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,  # поиск токена типа Bearer
    OAuth2PasswordBearer,  # упрощенный вариант выпуска токена
)
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel

from src.auth import utils as auth_utils
from src.schemas.todo_schemas import UserAuthSchema

# http_bearer = HTTPBearer() # помогает вытащить из заголовка авторизации тип Bearer
oauth2_scheme = OAuth2PasswordBearer( # выпускает точек используя адрес сам
    tokenUrl="/demo_jwt/login"
)

class TokenInfo(BaseModel): # схема для response в ответе на запрос
    access_token: str
    token_type: str

router = APIRouter(prefix="/demo_jwt", tags=["JWT"])

john = UserAuthSchema(
    username="John",
    password=auth_utils.hash_password("qwerty"),
    email="john@example.com",
    active=True,
)

sam = UserAuthSchema(
    username="Sam",
    password=auth_utils.hash_password("secret"),
    active=True,
)

# заполнение локальной базы данных через схему и данных по ней
users_db: dict[str, UserAuthSchema] = {
    john.username: john,
    sam.username: sam,
}

def validate_auth_user(
    username: str = Form(),
    password: str = Form(),

):
    """
    Функция для заполнения формы юзером
    """
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password"
    )
    if not (user := users_db.get(username)):
        raise unauthed_exc

    if not auth_utils.validate_password(
        password=password,
        hashed_password=user.password,
    ):
        raise unauthed_exc
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User inactive"
        )

    return user

def get_current_token_payload(
    # creds: HTTPAuthorizationCredentials = Depends(http_bearer),
    token: str = Depends(oauth2_scheme),

):
    """
    Берет токен из заголовка запроса
    Декодирует токен и возвращает полезную нагрузку
    """
    # token = creds.credentials # вытаскиевает токен используя http_bearer
    try:
        payload = auth_utils.decode_jwt(
            encoded_token=token,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error: {e}",
        )
    return payload

def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
) -> UserAuthSchema:
    """
    Поиск юзернейма в полученном токене и возврат его из функции
    """
    invalid_token = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalid (user not found)",
    )

    username = payload.get("sub") # проверка наличия в токене поля имени
    if not username:
        raise invalid_token

    user = users_db.get(username) # проверка наличия имени в БД
    if not user:
        raise invalid_token

    return user


def get_current_active_auth_user(
    user: UserAuthSchema = Depends(get_current_auth_user),
):
    """
    Получая пользователя проверяется его активация
    """
    if user.active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="user inactive"
    )


@router.post("/login", response_model=TokenInfo)
def auth_user_issue_jwt(
    user: UserAuthSchema = Depends(validate_auth_user),
):
    jwt_payload = {
        # "subject": user.id,  надо будет связать айди из БД
        "sub": user.username,
        "username": user.username,
        "email": user.email,
        # "logged_in_at":
    }
    token = auth_utils.encode_jwt(jwt_payload)
    return TokenInfo(
        access_token=token,
        token_type="Bearer",
    )

@router.get("/users/me")
def auth_user_check_self_info(
    payload: dict = Depends(get_current_token_payload), # берется кешированный пейлоад
    user: UserAuthSchema = Depends(get_current_active_auth_user),
):
    iat = payload.get("iat")
    return {
        "username": user.username,
        "email": user.email,
        "logged_in_at": iat,
    }
