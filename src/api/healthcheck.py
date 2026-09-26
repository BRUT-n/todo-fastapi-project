from fastapi import APIRouter, HTTPException, status

from src.database.crud.healthcheck import check_db_connection

router = APIRouter(prefix="/healthcheck", tags=["Healthcheck"])


@router.get(
    "/live",
    status_code=status.HTTP_200_OK,
    summary="Проверка доступности приложения",
    response_model=dict,
)
async def liveness_check():
    return {"status": "alive"}


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Проверка доступности базы данных",
    response_model=dict,
)
async def readiness_check():
    is_available = await check_db_connection()

    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="База данных недоступна",
        )

    return {"status": "ready"}
