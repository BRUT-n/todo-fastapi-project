from pathlib import Path # библиотека для работы с путями системы

from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
"""
Path - делает из пути объект. resolve - абсолютный путь. parent - аналог cd ..
"""

class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem" # !ненадежно указывать название папки!
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256" # ассиметричный алгоритм шифрования (публичный/приватный ключи)
    access_token_expire_minutes: int = 3 # время жизни токена в минутах

auth_config = AuthJWT()
