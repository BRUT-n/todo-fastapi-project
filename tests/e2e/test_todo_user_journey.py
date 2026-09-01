import httpx
import pytest
from fastapi import status

# ВАЖНО: Значение должно быть в диапазоне от 6 до 10,
# чтобы не ломались тесты пагинации (limit=5)
NUM_OF_LISTS_TO_CREATE = 6
NUM_OF_TASKS_TO_CREATE = 7


@pytest.mark.asyncio(loop_scope="session")
async def test_healthcheck_before_e2e(ac_online: httpx.AsyncClient):
    """Проверка доступности базы данных и тест работы /healthcheck."""
    response = await ac_online.get("/healthcheck")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_full_lifecycle_success(ac_online: httpx.AsyncClient):
    """
    Полный цикл работы приложения.
    Регистрация - логин - создание листа - создание задачи
     - отметка выполнения задачи - патч листа - патч задачи -
     - удаление листа - удаление пользователя.
    """
    # регистрация пользователя
    reg_payload = {
        "username": "e2e_username",
        "name": "Name",
        "password": "secret_password",
    }

    reg_response = await ac_online.post("/auth/register", json=reg_payload)

    assert reg_response.status_code == status.HTTP_201_CREATED

    auth_e2e_header = None

    try:
        # логин пользователя с получением токена
        login_payload = {
            "username": reg_payload["username"],
            "password": reg_payload["password"],
        }

        login_response = await ac_online.post("/auth/login", data=login_payload)

        assert login_response.status_code == status.HTTP_200_OK

        token = login_response.json()["access_token"]
        auth_e2e_header = {"Authorization": f"Bearer {token}"}

        # получение личных данных
        get_me_response = await ac_online.get("/auth/me", headers=auth_e2e_header)

        assert get_me_response.status_code == status.HTTP_200_OK

        # изменение данных пользователя
        patch_user_payload = {
            "username": "e2e_new_username",
            "name": "NewName",
            "email": "testmail@e2e.com",
        }

        patch_user_response = await ac_online.patch(
            "/me/profile", json=patch_user_payload, headers=auth_e2e_header
        )

        assert patch_user_response.status_code == status.HTTP_200_OK

        # создание нового листа
        todo_list_payload = {
            "title": "Список продуктов",
            "description": "Стол на корпоратив",
        }

        todo_list_response = await ac_online.post(
            "/me/to-do-lists", json=todo_list_payload, headers=auth_e2e_header
        )

        assert todo_list_response.status_code == status.HTTP_201_CREATED

        existing_todo_list = todo_list_response.json()

        # удаление листа
        delete_response = await ac_online.delete(
            f"/me/to-do-lists/{existing_todo_list['id_list']}", headers=auth_e2e_header
        )

        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # создание нескольких листов для пагинации
        created_many_lists = []

        for i in range(1, NUM_OF_LISTS_TO_CREATE + 1):
            many_lists_payload = {
                "title": f"Список №{i}",
                "description": f"Описание списка №{i}",
            }

            todo_list_in_many_response = await ac_online.post(
                "/me/to-do-lists", json=many_lists_payload, headers=auth_e2e_header
            )
            created_many_lists.append(todo_list_in_many_response.json())

        # проверка пагинации листов
        limit = 5
        get_lists_page_1_response = await ac_online.get(
            "/me/to-do-lists",
            headers=auth_e2e_header,
            params={"limit": limit, "offset": 0},
        )

        assert get_lists_page_1_response.status_code == status.HTTP_200_OK

        page_1 = get_lists_page_1_response.json()
        assert len(page_1) == limit

        get_lists_page_2_response = await ac_online.get(
            "/me/to-do-lists",
            headers=auth_e2e_header,
            params={"limit": limit, "offset": limit},
        )

        assert get_lists_page_2_response.status_code == status.HTTP_200_OK

        page_2 = get_lists_page_2_response.json()
        assert len(page_2) == NUM_OF_LISTS_TO_CREATE - limit  # зависит от созданных

        # изменение данных листа
        existing_list_id_for_lst_tests = created_many_lists[0]["id_list"]

        patch_list_payload = {"title": "NewTitle", "description": "NewDescription"}

        patch_list_response = await ac_online.patch(
            f"/me/to-do-lists/{existing_list_id_for_lst_tests}",
            json=patch_list_payload,
            headers=auth_e2e_header,
        )

        assert patch_list_response.status_code == status.HTTP_200_OK

        # создание задачи в существующем листе
        existing_list_id_for_tsk_tests = created_many_lists[1]["id_list"]
        task_payload = {"task_name": "Task_1", "completed": False}

        task_response = await ac_online.post(
            f"/me/to-do-lists/{existing_list_id_for_tsk_tests}/tasks",
            json=task_payload,
            headers=auth_e2e_header,
        )

        assert task_response.status_code == status.HTTP_201_CREATED

        existing_task = task_response.json()

        # удаление задачи в существующем листе
        delete_response = await ac_online.delete(
            f"/me/to-do-lists/{existing_list_id_for_tsk_tests}/tasks/{existing_task['id_task']}",
            headers=auth_e2e_header,
        )

        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # создание нескольких задач для пагинации
        created_many_tasks = []

        for i in range(1, NUM_OF_TASKS_TO_CREATE + 1):
            tasks_payload = {"task_name": f"Name №{i}", "completed": False}

            tasks_in_many_response = await ac_online.post(
                f"/me/to-do-lists/{existing_list_id_for_tsk_tests}/tasks",
                headers=auth_e2e_header,
                json=tasks_payload,
            )

            created_many_tasks.append(tasks_in_many_response.json())

        # проверка пагинации задач
        limit = 5
        get_tasks_page_1_response = await ac_online.get(
            f"/me/to-do-lists/{existing_list_id_for_tsk_tests}/tasks",
            headers=auth_e2e_header,
            params={"limit": limit, "offset": 0},
        )

        assert get_tasks_page_1_response.status_code == status.HTTP_200_OK

        page_1 = get_tasks_page_1_response.json()
        assert len(page_1) == limit

        get_tasks_page_2_response = await ac_online.get(
            f"/me/to-do-lists/{existing_list_id_for_tsk_tests}/tasks",
            headers=auth_e2e_header,
            params={"limit": limit, "offset": limit},
        )

        assert get_tasks_page_2_response.status_code == status.HTTP_200_OK

        page_2 = get_tasks_page_2_response.json()
        assert len(page_2) == NUM_OF_TASKS_TO_CREATE - limit  # зависит от созданных

        # изменение данных задачи
        existing_task_id = created_many_tasks[0]["id_task"]

        patch_task_payload = {"task_name": "NewName", "completed": True}

        patch_task_response = await ac_online.patch(
            f"/me/to-do-lists/{existing_list_id_for_tsk_tests}/tasks/{existing_task_id}",
            json=patch_task_payload,
            headers=auth_e2e_header,
        )

        assert patch_task_response.status_code == status.HTTP_200_OK

    finally:
        response = await ac_online.delete("/me/profile", headers=auth_e2e_header)

        assert response.status_code == status.HTTP_204_NO_CONTENT
