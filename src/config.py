from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_TITLE: str = "Todo List API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite+aiosqlite:///todo_lists.db"

    JWT_PRIVATE_KEY_PATH: Path = Path("certs/jwt-private-key.pem")
    JWT_PUBLIC_KEY_PATH: Path = Path("certs/jwt-public-key.pem")
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

print(f"DEBUG MODE IS: {settings.DEBUG}")
print(f"DATABASE URL IS: {settings.DATABASE_URL}")
