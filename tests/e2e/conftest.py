import pytest_asyncio
from httpx import AsyncClient
from src.database.config import settings

# Сервер Uvicorn запущен отдельно на порту 8000
E2E_BASE_URL = settings.app.E2E_BASE_URL


@pytest_asyncio.fixture(scope="function")
async def ac_online():
    """
    Асинхронный клиент для отправки HTTP-запросов к FastAPI на сервер
    """
    async with AsyncClient(base_url=E2E_BASE_URL) as client:
        yield client
