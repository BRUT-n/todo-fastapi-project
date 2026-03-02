from datetime import datetime, timedelta, timezone
from pathlib import Path

import bcrypt
import jwt

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PRIVATE_KEY_PATH = BASE_DIR / "certs" / "jwt-private-key.pem"
PUBLIC_KEY_PATH = BASE_DIR / "certs" / "jwt-public-key.pem"

PRIVATE_KEY = PRIVATE_KEY_PATH.read_text()
PUBLIC_KEY = PUBLIC_KEY_PATH.read_text()
ALGORITHM = "RS256"

def hash_password(
    password: str,
) -> bytes:
    """
    Хеширует пароль.
    gensalt - генерация в количестве 14 раз.
    encode - перевод пароля в байты.
    hashpw - хеширование.
    """
    salt = bcrypt.gensalt(rounds=14)
    password_to_bytes = password.encode()
    return bcrypt.hashpw(password_to_bytes, salt)

def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    """
    Сравнивает пароль с записанным хешом.
    checkpw - на основе данных в хеше прогоняет пароль еще раз
    и сравнивает полученный хеш с верным.
    """
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )

def encode_jwt_token(
    payload: dict,
    private_key: str,
    algorithm: str,
    expire_minutes: int,
    expire_time_delta: timedelta | None = None,
):
    """
    Создает токен.
    payload - какую информацию вкладывать в токен.
    """
    encoded_payload = payload.copy()
    now = datetime.now(tz=timezone.utc)

    if expire_time_delta:
        expire = now + expire_time_delta
    else:
        expire = now + timedelta(expire_minutes)

    encoded_payload.update(
        exp=expire,
        iat=now,
    )

    token = jwt.encode(
        encoded_payload,
        private_key,
        algorithm,
    )
    return token

def decode_jwt_token(
    encoded_token: str,
    public_key: str,
    algorithm: str,
):
    """
    Расшифровка токена с автоматической проверкой целостности,
    срока годности.
    """
    decoded_token = jwt.decode(
        encoded_token,
        public_key,
        algorithms=[algorithm] # обязательно так, из-за обновы безопасности
    )
    return decoded_token

