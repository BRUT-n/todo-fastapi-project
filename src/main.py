from fastapi import FastAPI
from src.api.routers import all_router
from contextlib import asynccontextmanager
from src.database import engine, Base

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

# 2. Подключаем логику к приложению
app = FastAPI(lifespan=lifespan)

app.include_router(all_router)
