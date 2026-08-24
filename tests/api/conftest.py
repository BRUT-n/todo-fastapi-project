import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from src.auth.utils import encode_jwt_token
from src.main import app


@pytest_asyncio.fixture(scope="function")
async def ac():
    """
    Асинхронный клиент для отправки HTTP-запросов к FastAPI в памяти (не по сети)
    """
    transport = ASGITransport(app=app) # транспорт для отправки запросов напрямую к приложению, идут в память, а не в сеть
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture(scope="function")
async def auth_header(create_test_user):
    existing_user_id = create_test_user.id_user
    payload = {"sub": str(existing_user_id)}

    token = encode_jwt_token(payload=payload)
    return {"Authorization": f"Bearer {token}"}
