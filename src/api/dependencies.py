from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
'''
Depends используется для объявления того, что определенная функция (обработчик маршрута, path operation function)
или другая зависимость требует для своей работы результаты выполнения другой функции или класса
AsyncSession - Это тип объекта. Это само «соединение» (ключ).
Depends(get_session): Это инструкция для FastAPI.
«Прежде чем запустить функцию, пойди и запусти функцию get_session, возьми то, что она вернет, и подставь сюда».
Annotated[...]: Это просто «упаковка». Мы объединяем тип и инструкцию в одну удобную переменную SessionDep.
'''
