from fastapi import HTTPException, status


class BaseAppException(HTTPException):
    """
    Родительский класс для отслеживания всех ошибок приложения.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Внутренняя ошибка приложения"

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)

class AuthException(BaseAppException):
    """Базовый класс для ошибки авторизации"""
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Аутентификация не пройдена"

    def __init__(self):
        super().__init__()

class InvalidCredentialsException(AuthException):
    detail = "Неверный логин или пароль"

    def __init__(self):
        super().__init__()

class TokenExpiredException(AuthException):
    detail = "Токен просрочен, необходимо войти повторно"

    def __init__(self):
        super().__init__()

class TokenInvalidException(AuthException):
    detail = "Невалидный токен"

    def __init__(self):
        super().__init__()

class TokenMissingSubException(AuthException):
    detail = "В токене отсутствует необходимый sub"

    def __init__(self):
        super().__init__()

class TokenUserNotFoundException(AuthException):
    detail = "Пользователь токена не найдет"

    def __init__(self):
        super().__init__()

class AlreadyRegisteredException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь с таким email уже существует"

    def __init__(self):
        super().__init__()

class UserNotFoundException(BaseAppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Пользователь не найден"

    def __init__(self):
        super().__init__()
