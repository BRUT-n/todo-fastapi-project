from fastapi import (  # для формы нужен python-multipart
    APIRouter,
    Depends,
    Form,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,  # поиск токена типа Bearer в загаловке запроса
    OAuth2PasswordBearer,  # упрощенный вариант выпуска токена
)
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel

from src.auth import utils as auth_utils
from src.schemas.todo_schemas import UserAuthSchema

# http_bearer = HTTPBearer() # помогает вытащить из заголовка авторизации тип Bearer
oauth2_scheme = OAuth2PasswordBearer( # выпускает токен используя адрес сам
    tokenUrl="/demo_jwt/login" # адрес, где выпускается токен
)

class TokenInfo(BaseModel): # схема для response в ответе на запрос
    access_token: str
    token_type: str

router = APIRouter(prefix="/demo_jwt", tags=["JWT"])

john = UserAuthSchema(
    username="John",
    password=auth_utils.hash_password("qwerty"), # сразу хеширование пароля в байтах (т.к. функция отдает в байтах)
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
    username: str = Form(), # Form для совместимости с OAuth2 и работы с кнопкой "Authorize" в Swagger
    password: str = Form(),

):
    """
    Функция для заполнения формы юзером, проверки аутентфикации и статуса аккаунта.
    """
    unauthed_exc = HTTPException( # одна и та же ошибка под разные сценарии для защиты от перебора
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password"
    )
    if not (user := users_db.get(username)): # если НЕ (пользователь = юзернейм из базы)
        raise unauthed_exc

    if not auth_utils.validate_password( # проверка пароля: совпадение полученного и хешированного
        password=password, # полученый пароль становится хешем через bcrypt
        hashed_password=user.password, # пароль из базы (в байтах) для сравнения с полученным
    ):
        raise unauthed_exc

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User inactive"
        )

    return user

def get_current_token_payload(
    # creds: HTTPAuthorizationCredentials = Depends(http_bearer), # не привязан к url, а просто берет введенный токен (как на гите)
    token: str = Depends(oauth2_scheme), # протокол извлечения токена с привязкой к url (не нужно самому его вытаскивать, берется из url)
):
    """
    Берет токен либо из заголовка (HTTPBearer), неважно откуда он приходит.
    Либо по указанному url (oauth2_scheme), важна работа с формой логина (username+password) чтобы выпустить токен.
    Декодирует токен и возвращает полезную нагрузку (айди, имя, время логина и тд)
    """
    # token = creds.credentials # вытаскивает токен используя http_bearer
    try:
        payload = auth_utils.decode_jwt(
            encoded_token=token,
        )
    except InvalidTokenError as error: # ловит ошибки токена (срок, не валидный, формат не JSON)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error: {error}", # явно показывает ошибку - не безопасно в реальности
        )
    return payload # возврат раскодированных данных пользователя (что было зашито в токен)

def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
) -> UserAuthSchema:
    """
    Получает токен из инъекции зависимости и работает с ним.
    Поиск в токене уникального "sub" - первая проверка.
    Поиск в базе по "sub" конкретного пользователя - вторая проверка.
    Если все проверено успешно возвращает данные пользователя по схеме.
    """
    invalid_token = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalid (user not found)",
    )

    username_id = payload.get("sub") # проверка наличия в токене поля имени Subject по стандарту (обязательное и уникальное)
    if not username_id:
        raise invalid_token # если в токене зашит неверный айди, то токен не принят

    user = users_db.get(username_id)  # проверка на актуальность (проверяет в БД) чтобы исключить ситуации - токен есть, но из базы уже удален юзер
    if not user:
        raise invalid_token # если токен имеет верный айди, но в базе нет юзера с таким айди (удален, заблокирован) - токен не принят

    return user # возврат полных данный пользователя (как условное окно "мой профиль") согласно указанной схеме


def get_current_active_auth_user(
    user: UserAuthSchema = Depends(get_current_auth_user),
):
    """
    Получает всю информацию (схему) о пользователе из зависимости.
    Проверяет его статус - активен/не активен.
    """
    if user.active: # вытаскивает из схемы поле актива - тру/фолс
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User inactive"
    )


@router.post("/login", response_model=TokenInfo)
def auth_user_issue_jwt(
    user: UserAuthSchema = Depends(validate_auth_user),
):
    jwt_payload = {
        # "subject": user.id,  надо будет связать айди из БД
        "sub": user.username, # примерный вариант заполнения
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
