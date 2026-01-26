import secrets  # Библиотека для безопасной работы с секретами (защита от атак по времени)
import uuid
from time import time
from typing import Annotated, Any  # Стандарт Python для добавления метаданных к типам

from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Response, status
from fastapi.security import (  # HTTPBasic — это схема (логика), HTTPBasicCredentials — это структура данных (логин/пароль)
    HTTPBasic,
    HTTPBasicCredentials,
)

router = APIRouter(prefix="/demo-auth", tags=["Demo Auth"]) # отдельная группа маршрутов с общим префиксом

# Инициализируем систему Basic Auth. 
# Когда мы передадим это в Depends security, FastAPI поймет: нужно искать заголовок 'Authorization: Basic ...'
security = HTTPBasic() # экземпляр класса, говорит FastAPI проверить заголовок Authorization - если пусто то сразу 401
# после 401 выдает окно авторизации для ввода логин/пароль

@router.get("/basic-auth")
def demo_basic_credentials(
    # Annotated говорит: переменная 'credentials' имеет тип 'HTTPBasicCredentials',
    # а получить её нужно через зависимость 'security' перед тем как запустить функцию
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    # Если мы попали сюда, значит FastAPI уже проверил наличие заголовка.
    # Если заголовка не было, клиент получил 401 автоматически, код ниже не выполнится.
    return {
        "message": "HI",
        "username": credentials.username,
        "password": credentials.password,
    }



# Имитация базы данных пользователей
usernames_to_password = {
    "admin": "admin",
    "john": "password",
}

# Это наша кастомная ЗАВИСИМОСТЬ. Она проверяет, есть ли пользователь в нашей "базе"
def get_auth_user_username(
    # Она сама зависит от 'security', то есть сначала достает данные из заголовка
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    # Заранее готовим ошибку, которую будем выкидывать при неудаче
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        # Заголовок WWW-Authenticate заставляет браузер показать окно ввода логина/пароля
        headers={"WWW-Authenticate": "Basic"}, # WWW-Authenticate — обязателен для Basic Auth без него браузер не покажет окно логина
    )

    # Пытаемся найти пароль для введенного имени пользователя
    correct_password = usernames_to_password.get(credentials.username)

    # Если такого пользователя нет — прерываем выполнение и отдаем 401
    if correct_password is None:
        raise unauthed_exc

    # Безопасное сравнение паролей (защита от Side-channel атак)
    # .encode("utf-8") переводит строки в байты, так как secrets работает с ними
    if not secrets.compare_digest( # сравнивает значения безопасно (одинаково по времени)
        credentials.password.encode("utf-8"),
        correct_password.encode("utf-8"),
    ):
        raise unauthed_exc

    # Если всё верно, возвращаем только имя пользователя.
    # Это значение "провалится" в основную функцию ниже.
    return credentials.username


@router.get("/basic-auth-username")
def demo_basic_auth_username(
    # Здесь магия Depends: FastAPI видит, что нам нужно 'auth_username'.
    # Он запускает 'get_auth_user_username', та запускает 'security'.
    # Если вся цепочка прошла успешно, мы получаем строку с именем пользователя.
    auth_username: str = Depends(get_auth_user_username),
):
    # К этому моменту пользователь ГАРАНТИРОВАННО прошел проверку.
    # Нам не нужно писать if-else внутри этой функции.
    return {
        "message": f"Hi, {auth_username}",
        "username": auth_username,
    }



# Имитация базы данных пользователей с токеном
static_auth_token_username = {
    "696e23458b2b51123e9db44cf233ca3b": "admin",
    "c3ad9e797abcdbf546ab0a0872bf4bb5": "john",
}

def get_username_by_static_auth_token( # фукнция проверки на соответсвие токену
    static_token: str = Header(alias="x_auth_token"), # ищи в HTTP-заголовках ключ "x_auth_token". возьми его и положи в static_token
) -> str:
    if username := static_auth_token_username.get(static_token): # есть токен есть юзернаме = гет значения
        return username

    raise HTTPException( # иначе ошибка
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalid"
    )


@router.get("/some-http-header-auth")
def demo_auth_some_http_header(
    username: str = Depends(get_username_by_static_auth_token),
):
    # К этому моменту пользователь ГАРАНТИРОВАННО прошел проверку.
    # Нам не нужно писать if-else внутри этой функции.
    return {
        "message": f"Hi, {username}",
        "username": username,
    }

'''
Запрос: Пользователь заходит на /login-cookie и вводит пароль.
Проверка: Depends проверяет пароль и говорит: «Ок, это юзер Ivan».
Генерация: Сервер создает случайный код xyz.
Память: Сервер записывает в COOKIES: xyz — это Ivan.
Ответ: Сервер отдает ответ и говорит браузеру: «Запомни код xyz».
Будущее: Когда Ivan придет завтра, его браузер пришлет код xyz. 
Сервер заглянет в свой словарь COOKIES, увидит там xyz и сразу поймет 
— это Ivan, пароль спрашивать снова не нужно!
'''
# сюда записывается уникальынй айди : словарь указанных данных
COOKIES: dict[str, dict[str, Any]] = {} # словарь с аннотацией для хранения кук, хранится в оперативке

COOKIE_SESSION_ID_KEY = "web-app-session-id" # имя кук, их видит и запоминает браузер
# при обрачении к сайт, сайт просит у браузера то, что он запомнил и сверяет с пользователями

def generate_session_id() -> str: # случайная генерация айди сессии
    return uuid.uuid4().hex

def get_session_data(
    session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY), # смотрит в cookies, ищет web-app-session-id, кладёт значение в session_id
):
    if session_id not in COOKIES: # если  нет в куках - пользователь не авторизован
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not authenticated"
        )

    return COOKIES[session_id]

@router.get("/login-cookie")
def demo_auth_login_set_cookies(
    response: Response, # Response это заготовка - будет ответ на базе класса с нужными данными
    auth_username: str = Depends(get_auth_user_username), # можно выбирать методы логина через зависимости функций выше
    # username: str = Depends(get_username_by_static_auth_token),
):
    session_id = generate_session_id()
    COOKIES[session_id] = { # запись данных(какие нужны) в словарь для кук
        "username": auth_username,
        "login_at": int(time()),
    }
    response.set_cookie(COOKIE_SESSION_ID_KEY, session_id) # в ответе команда браузеру запомнить ключ со значением из ответа
    return {"ok":"true"}

@router.get("/check-cookie")
def demo_auth_check_cookie(
    user_session_data: dict = Depends(get_session_data), # если код дошел сюда, есть валидные куки, пользов-ль аутент-н
):
    username = user_session_data["username"] # вытаскивается имя
    return {
        "message": f"Hello, {username}",
        **user_session_data,
    }

@router.get("/logout-cookie")
def demo_auth_logout_cookie(
    response: Response,
    session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY),
    user_session_data: dict = Depends(get_session_data),
):
    COOKIES.pop(session_id) # удаление сессии на сервере
    response.delete_cookie(COOKIE_SESSION_ID_KEY) # команда браузеру "удали куки"
    username = user_session_data["username"]
    return {
        "message": f"By, {username}",
    }
