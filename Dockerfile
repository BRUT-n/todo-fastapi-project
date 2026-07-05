FROM python:3.12-slim

# загрузка из гитхаба официального uv (uvx доп утилита, bin папка в контейнере)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# копирует зависимости с локальной машины в докер
COPY pyproject.toml uv.lock ./

# синхронизация пакетов без проверки обновлений
RUN uv sync --frozen

# копирование всего кода приложения в докер app/src/
COPY src/ ./src
COPY certs/ ./certs

# подсказывает порт на котором ждет приложение
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]