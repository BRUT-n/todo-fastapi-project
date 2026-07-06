FROM python:3.12-slim

# запрет на создание __pycache__ и файлы .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# отключение буферизации вывода, выводит логи сразу в терминал докера
ENV PYTHONUNBUFFERED=1

# загрузка из гитхаба официального uv (uvx доп утилита, bin папка в контейнере)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# копирует зависимости с локальной машины в докер
COPY pyproject.toml uv.lock ./

# синхронизация пакетов uv без проверки обновлений, запрет на добавление --dev раздела и комп.файлов
RUN uv sync --frozen --no-dev --no-compile

# копирование всего кода приложения в докер app/src/
COPY src/ ./src
COPY certs/ ./certs

# подсказывает порт на котором ждет приложение
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
