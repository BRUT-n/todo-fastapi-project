from fastapi import APIRouter
from src.api.tasks import router as tasks_router
from src.api.todo_lists import router as todo_list_router
from src.api.users import router as user_router
from src.demo_auth.views import router as demo_auth_router

all_router = APIRouter() # базовый роутер для всего АПИ

# подключение всех модулей (роутеров) в один главный
all_router.include_router(user_router)
all_router.include_router(todo_list_router)
all_router.include_router(tasks_router)
all_router.include_router(demo_auth_router)
