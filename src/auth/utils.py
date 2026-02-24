from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from src.auth.config import auth_config

# private_key = b"-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAwhvqCC+37A+UXgcvDl+7nbVjDI3QErdZBkI1VypVBMk"
# public_key = b"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwhvqCC+37A+UXgcvDl+7\"
# encoded = jwt.encode({"some": "payload"}, private_key, algorithm="RS256")
# decoded = jwt.decode(encoded, public_key, algorithms=["RS256"])

def encode_jwt(
    payload: dict,
    private_key: str = auth_config.private_key_path.read_text(), # читает текст ключа из пути (один раз - статически)
    algorithm: str = auth_config.algorithm,
    expire_minutes: int = auth_config.access_token_expire_minutes, # стандартно по схеме в классе
    expire_time_delta: timedelta | None = None # опционально можно указать нужное время. timedelta - по сути это отрезок времени
):
    """
    Функция создания токена.
    Кодирование токена на основе:
    "полезной нагрузки" - что будет включать в себя jwt
    приватного ключа - сгенерированного отдельно
    алгоритма - указанного при генерации ключа
    """
    payload_to_encode = payload.copy() # принято работать с копией, чтобы не менять исходный словарь
    now = datetime.now(tz=timezone.utc) # текущее время чтобы к нему прибавлять, utc - формат времени без часовых поясов
    if expire_time_delta: # проверка опционального аргумента
        expire = now + expire_time_delta # истекает сейчас+аргумент
    else:
        expire = now + timedelta(minutes=expire_minutes) # истекает сейчас+стандартный

    # регистрация прав (Claims)
    payload_to_encode.update( # обновление словаря нагрузки по указанному времени
        exp=expire, # истекает через
        iat=now, # когда создан
    )

    # подпись токена - кодирование его из полезной нагрузки, приват ключа и алгоритма
    encoded = jwt.encode(
        payload_to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded

def decode_jwt(
    encoded_token: str | bytes,
    public_key: str = auth_config.public_key_path.read_text(),
    algorithm: str = auth_config.algorithm,
):
    """
    Функция проверки токена.
    Автоматически проверяет целостность (нагрузка+паблик_кей).
    Автоматически проверяет срок годности (expire).
    После проверок декодирует в пайтон-словарь.
    Декодирование пароля на основе:
    закодированного токена - либо строка либо байты
    публичного ключа - сгенерированного отдельно
    алгоритма - указанного при генерации ключа
    """
    decoded_token = jwt.decode(
        encoded_token,
        public_key,
        algorithms=[algorithm] # PyJWT принимает только algorithms и строго ограничивает ввод алгоритмов
    )
    return decoded_token



def hash_password(
    password: str,
) -> bytes:
    """
    Хеширование пароля с использование соли
    """
    salt = bcrypt.gensalt(rounds=14) # генерирует соль (по умолчанию 12 итераций)
    pwd_bytes: bytes = password.encode() # кодируют пароль в байты т.к. bcrypt работает только с набором байтов
    # hashed_pwd_str = pwd_bytes.decode('utf-8') # перевод в строку для хранения в БД
    return bcrypt.hashpw(pwd_bytes, salt) # солит и хеширует всё


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    """
    Проверка пароля на основе:
    чистого пароля который ввел юзер
    хешированного пароля - который берется из БД
    !пароли не расхешируются!
    """
    return bcrypt.checkpw(
        password=password.encode(), # перевод в байты т.к. криптография работает с байтами
        hashed_password=hashed_password,
    )
    # checkpw - берет хеш (первые символы - алгоритм и стоимость) и прогоняет через алгоритм хеширование введенный пароль
    # encode переводит в байты,
    # hashed_password - хеш из базы
