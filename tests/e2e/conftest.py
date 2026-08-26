import pytest_asyncio
from httpx import AsyncClient

# Сервер Uvicorn запущен отдельно на порту 8000
E2E_BASE_URL = "http://127.0.0.1:8000"

@pytest_asyncio.fixture(scope="function")
async def ac_online():
    """
    Асинхронный клиент для отправки HTTP-запросов к FastAPI на сервер
    """
    async with AsyncClient(base_url=E2E_BASE_URL) as client:
        yield client
