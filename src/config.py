from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseModel):
    TITLE: str = "Todo List Manager API"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    # для тестов е2е
    E2E_BASE_URL: str = "http://127.0.0.1:8000"


# TODO: добавить автогенерацию версий приложения


class DataBaseSettings(BaseModel):
    URL: str = "postgresql+asyncpg://brutn:brutn@localhost:5432/todo_app_db"


class AuthSettings(BaseModel):
    JWT_PRIVATE_KEY_PATH: Path = Path("certs/jwt-private-key.pem")
    JWT_PUBLIC_KEY_PATH: Path = Path("certs/jwt-public-key.pem")
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    BCRYPT_ROUNDS: int = 4


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    db: DataBaseSettings = DataBaseSettings()
    auth: AuthSettings = AuthSettings()

    model_config = SettingsConfigDict(
        env_file=".env", env_nested_delimiter="__", extra="ignore"
    )


settings = Settings()


print(f"DEBUG MODE IS: {settings.app.DEBUG}")
print(f"DATABASE URL IS: {settings.db.URL}")
print(f"TITLE IS: {settings.app.TITLE}")
