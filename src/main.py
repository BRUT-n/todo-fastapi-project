from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routers import all_router
from src.config import settings
from src.database.config import Base, engine
from src.logger_config import setup_logging
from src.middleware import (
    metrics_asgi_app,
    observability_middleware,
)


# 1. Декоратор превращает функцию в "контекстный менеджер"
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- ЭТО БЛОК STARTUP (Выполняется один раз при старте) ---
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield  # Разделитель. В этой точке FastAPI начинает слушать запросы.

    # --- ЭТО БЛОК SHUTDOWN (Выполняется один раз при выключении) ---
    await engine.dispose()  # закрывает каналы связи


# Подключаем логику к приложению
app = FastAPI(
    lifespan=lifespan,
    title=settings.app.TITLE,
    version=settings.app.VERSION,
    debug=settings.app.DEBUG,
)

# Инициализируем логи по правилам окружения
setup_logging()

app.middleware("http")(observability_middleware)
# app.middleware("http")(log_new_request)
# app.middleware("http")(add_process_time_to_requests)

app.include_router(all_router)
# .mount() метод FastAPI, позволяет "вмонтировать" другое ASGI-приложение внутрь вашего.
# при переходе на URL "/metrics", FastAPI передаст управление библиотеке Prometheus.
app.mount("/metrics", metrics_asgi_app)
