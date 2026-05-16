from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routers import all_router
from src.config import settings
from src.database.config import Base, engine


# 1. Декоратор превращает функцию в "контекстный менеджер"
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- ЭТО БЛОК STARTUP (Выполняется один раз при старте) ---
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield # Разделитель. В этой точке FastAPI начинает слушать запросы.

    # --- ЭТО БЛОК SHUTDOWN (Выполняется один раз при выключении) ---
    await engine.dispose() # закрывает каналы связи

# Подключаем логику к приложению
app = FastAPI(
    lifespan=lifespan,
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

app.include_router(all_router)
