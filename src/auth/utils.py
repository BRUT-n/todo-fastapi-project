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
    private_key: str = auth_config.private_key_path.read_text(),
    algorithm: str = auth_config.algorithm,
    expire_minutes: int = auth_config.access_token_expire_minutes, # стандартно по схеме в классе
    expire_time_delta: timedelta | None = None # можно указать нужное время
):
    """
    Функция кодировки пароля на основе:
    "полезной нагрузки" - что будет включать в себя jwt
    приватного ключа - сгенерированного отдельно
    алгоритма - указанного при генерации ключа
    """
    to_encode = payload.copy() # принято работать с копией
    now = datetime.now(tz=timezone.utc) # текущее время чтобы к нему прибавлять
    if expire_time_delta:
        expire = now + expire_time_delta # если арг. указан
    else:
        expire = now + timedelta(minutes=expire_minutes) # если нет - стандарный
    to_encode.update( # обновление словаря нагрузки по указанному времени
        exp=expire,
        iat=now, # когда создан
    )
    encoded = jwt.encode(
        to_encode,
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
    Функция раскодирования пароля на основе:
    закодированного токена - либо строка либо байты
    публичного ключа - сгенерированного отдельно
    алгоритма - указанного при генерации ключа
    """
    decoded = jwt.decode(
        encoded_token,
        public_key,
        algorithms=[algorithm]
    )
    return decoded



def hash_password(
    password: str,
) -> bytes:
    """
    Хеширование пароля с использование соли
    """
    salt = bcrypt.gensalt() # генерирует соль
    pwd_bytes: bytes = password.encode() # кодируют пароль в байты
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
        password=password.encode(),
        hashed_password=hashed_password,
    ) # checkpw - очищает от соли, encode переводит в байты, hashed_password - хеш из базы
