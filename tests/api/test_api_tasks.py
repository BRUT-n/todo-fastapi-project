import pytest
from fastapi import status
from httpx import AsyncClient
from pydantic import TypeAdapter
from src.models.schemas import TaskResponseSchema


@pytest.mark.asyncio(loop_scope="session")
async def test_create_task_success(ac: AsyncClient, auth_header, create_test_todo_list):
    """
    Проверка успешного создания задачи авторизированного пользователя.
    """
    existing_list_id = create_test_todo_list.id_list
    payload = {"task_name": "Task_1", "completed": False}

    response = await ac.post(
        f"/me/to-do-lists/{existing_list_id}/tasks", json=payload, headers=auth_header
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    # assert TaskResponseSchema.model_validate(data)
    assert isinstance(data["id_task"], int)
    assert data["task_name"] == payload["task_name"]
    assert data["completed"] == payload["completed"]


@pytest.mark.asyncio(loop_scope="session")
async def test_create_task_nonexistent_list(ac: AsyncClient, auth_header):
    """
    Проверка ошибки несуществующего листа задач.
    """
    payload = {"task_name": "SomeTask"}

    response = await ac.post(
        "/me/to-do-lists/99999/tasks", json=payload, headers=auth_header
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    data = response.json()
    assert data["detail"] == "User or list not found"


@pytest.mark.parametrize(
    "bad_payload",
    [
        {"task_name": "T"},
        {"task_name": "T" * 65},
        {"task_name": "OK", "completed": "Yes"},
        {},
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_create_task_incorrect_payload(
    ac: AsyncClient, auth_header, create_test_task, bad_payload
):
    """
    Проверка валидации согласно схеме TaskAddSchema и ее условиям.
    """
    existing_list_id = create_test_task.list_id

    response = await ac.post(
        f"/me/to-do-lists/{existing_list_id}/tasks",
        json=bad_payload,
        headers=auth_header,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio(loop_scope="session")
async def test_create_task_unauthorized(ac: AsyncClient):
    """
    Проверка ошибки создания задачи неавторизированного пользователя.
    """
    response = await ac.post("/me/to-do-lists/1/tasks", json={"task_name": "any"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio(loop_scope="session")
async def test_get_tasks_with_pagination(
    ac: AsyncClient, auth_header, create_many_test_tasks
):
    """
    Проверка вывода всех задач листа с пагинацией.
    """
    tasks = await create_many_test_tasks(count=10)
    existing_list_id = tasks[0].list_id

    response = await ac.get(
        f"/me/to-do-lists/{existing_list_id}/tasks",
        headers=auth_header,
        params={"limit": 5, "offset": 6},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 4
    assert TypeAdapter(list[TaskResponseSchema]).validate_python(data)


@pytest.mark.parametrize("limit, offset", [(0, 0), (25, 0), ("a", "b")])
@pytest.mark.asyncio(loop_scope="session")
async def test_get_tasks_with_incorrect_pagination_params(
    ac: AsyncClient, auth_header, create_test_todo_list, limit, offset
):
    """
    Проверка ошибки при некорректных параметров пагинации.
    """
    existing_list_id = create_test_todo_list.id_list
    response = await ac.get(
        f"/me/to-do-lists/{existing_list_id}/tasks",
        headers=auth_header,
        params={"limit": limit, "offset": offset},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio(loop_scope="session")
async def test_get_tasks_unauthorized(ac: AsyncClient):
    """
    Проверка ошибки неавторизованного пользователя.
    """
    response = await ac.get(
        "/me/to-do-lists/1/tasks",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "payload, expected_name, expected_status",
    [
        ({"task_name": "NewName", "completed": True}, "NewName", True),
        ({"task_name": "OnlyName"}, "OnlyName", False),
        ({"completed": True}, "TaskName", True),
        ({}, "TaskName", False),
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_patch_task_success(
    ac: AsyncClient,
    auth_header,
    create_test_task,
    payload,
    expected_name,
    expected_status,
):
    """
    Успешное изменение задачи по всем параметрам.
    """
    existing_list_id = create_test_task.list_id
    existing_task_id = create_test_task.id_task

    response = await ac.patch(
        f"/me/to-do-lists/{existing_list_id}/tasks/{existing_task_id}",
        json=payload,
        headers=auth_header,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    # assert TaskResponseSchema.model_validate(data)
    assert data["task_name"] == expected_name
    assert data["completed"] == expected_status


@pytest.mark.parametrize(
    "bad_payload",
    [
        {"task_name": "ml"},
        {"completed": "completed"},
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_patch_task_incorrect_payload(
    ac: AsyncClient, auth_header, create_test_task, bad_payload
):
    """
    Проверка валидации согласно схеме TaskPatchSchema и ее условиям.
    """
    existing_list_id = create_test_task.list_id
    existing_task_id = create_test_task.id_task

    response = await ac.patch(
        f"/me/to-do-lists/{existing_list_id}/tasks/{existing_task_id}",
        json=bad_payload,
        headers=auth_header,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_task_not_found(
    ac: AsyncClient, auth_header, create_test_todo_list
):
    """
    Проверка ошибки ненайденной задачи.
    """
    existing_list_id = create_test_todo_list.id_list

    response = await ac.patch(
        f"/me/to-do-lists/{existing_list_id}/tasks/99999",
        json={"task_name": "any-name"},
        headers=auth_header,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_task_unauthorized(ac: AsyncClient):
    """
    Проверка ошибки неавторизованного пользователя.
    """

    response = await ac.patch(
        "/me/to-do-lists/1/tasks/1",
        json={"task_name": "anyname"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_task_success(ac: AsyncClient, auth_header, create_test_task):
    """
    Успешное удаление задачи.
    """
    existing_list_id = create_test_task.list_id
    existing_task_id = create_test_task.id_task

    response = await ac.delete(
        f"/me/to-do-lists/{existing_list_id}/tasks/{existing_task_id}",
        headers=auth_header,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not response.content

    all_tasks = await ac.get(
        f"/me/to-do-lists/{existing_list_id}/tasks",
        headers=auth_header,
        params={"limit": 5},
    )

    data = all_tasks.json()
    all_ids = [tasks["id_task"] for tasks in data]
    assert existing_task_id not in all_ids


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_task_not_found(
    ac: AsyncClient, auth_header, create_test_todo_list
):
    """
    Проверка ошибки несуществующей задачи.
    """
    existing_list_id = create_test_todo_list.id_list

    response = await ac.delete(
        f"/me/to-do-lists/{existing_list_id}/tasks/99999", headers=auth_header
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_task_unauthorized(ac: AsyncClient):
    """
    Проверка ошибки удаления задачи неавторизованным пользователем.
    """

    response = await ac.delete(
        "/me/to-do-lists/1/tasks/1",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
