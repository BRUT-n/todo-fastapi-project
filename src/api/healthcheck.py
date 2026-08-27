from fastapi import APIRouter, HTTPException, status

from src.database.crud.healthcheck import check_db_connection

router = APIRouter(prefix="/healthcheck", tags=["Healthcheck"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Проверка доступности базы данных",
    response_model=dict,
)
async def healthcheck():
    is_available = await check_db_connection()

    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="База данных недоступна",
        )

    return {"status": "ok"}
