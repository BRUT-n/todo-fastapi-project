import pytest
from src.database.crud.healthcheck import check_db_connection


@pytest.mark.asyncio(loop_scope="session")
async def test_check_db_connection_success():
    result = await check_db_connection()

    assert result is True


@pytest.mark.filterwarnings("ignore:transaction already deassociated")
@pytest.mark.asyncio(loop_scope="session")
async def test_check_db_connection_failure(test_connection):

    await test_connection.close() # принудительное закрытие подключения из conftest

    result = await check_db_connection()
    assert result is False
