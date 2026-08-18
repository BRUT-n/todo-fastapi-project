from sqlalchemy import text
from src.database.config import session_factory


async def check_db_connection() -> bool:
    try:
        async with session_factory() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception:
        return False
