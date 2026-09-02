import tomllib  # парсинг .toml и перевод их в словари (dict).
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_version_from_pyproject() -> str:
    """
    Читает актуальную версию напрямую из pyproject.toml.
    Работает и локально, и внутри Docker-контейнера.
    """
    # 1. Path(__file__) берет путь к текущему файлу (config.py).
    # 2. .resolve() делает путь абсолютным (начиная от корня диска,
    # например C:/.../src/config.py)
    # 3. Каждое .parent поднимает нас на одну папку вверх:
    # 4. / "pyproject.toml" добавляет имя файла к пути.
    pyproject_path = Path(__file__).resolve().parent / "pyproject.toml"

    try:
        # Проверяем, существует ли файл по этому пути
        if pyproject_path.exists():

            # Открываем файл. "rb" значит "read binary" (читать в бинарном режиме).
            # tomllib требует именно бинарного чтения, исключая проблем кодировок
            with open(pyproject_path, "rb") as f:

                # tomllib.load(f) читает весь файл и превращает его в Python-словарь.
                # data будет выглядеть так: {"project":
                # {"name": "todo-app", "version": "0.1.0"}, ...}
                data = tomllib.load(f)

                # Идем по словарю. .get("project", {}) ищет ключ "project".
                # Если не найдет, вернет пустой словарь {}.
                # Следующий .get("version", "0.1.0-dev") ищет версию.
                # Если не найдет, вернет "0.1.0-dev" как страховку.
                return data.get("project", {}).get("version", "0.1.0-dev")
    except Exception:
        pass

    return "0.1.0-dev"

class AppSettings(BaseModel):
    TITLE: str = "Todo List Manager API"
    DEBUG: bool = False
    VERSION: str = get_version_from_pyproject()
    # для тестов е2е
    E2E_BASE_URL: str = "http://127.0.0.1:8000"


    # VERSION: str = "0.1.0"
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
