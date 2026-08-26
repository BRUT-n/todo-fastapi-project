import pytest
from fastapi import status
from httpx import AsyncClient
from pydantic import TypeAdapter
from src.models.schemas import ListResponseSchema


@pytest.mark.asyncio(loop_scope="session")
async def test_post_new_list_success(ac: AsyncClient, auth_header: dict):
    """
    Проверка успешного создания листа авторизированного пользователя.
    """
    payload = {
        "title" : "Список продуктов",
        "description" : "Продукты на праздник"
    }

    response = await ac.post(
        "/me/to-do-lists",
        json=payload,
        headers=auth_header
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    # assert ListResponseSchema.model_validate(data)
    assert data["id_list"] is not None
    assert isinstance(data["id_list"], int)
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    "empty_payload",
    [
        {"title" : ""},
        {"description" : ""}
    ]
)
async def test_post_new_list_empty_data(ac: AsyncClient, empty_payload, auth_header: dict):
    """
    Валидация полей - минимальная длина 1 символ
    """
    response = await ac.post(
        "/me/to-do-lists",
        json=empty_payload,
        headers=auth_header,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio(loop_scope="session")
async def test_post_new_list_unauthorized(ac: AsyncClient):
    """
    Проверка ошибки создания листа неавторизированного пользователя.
    """
    payload = {
        "title" : "Список",
        "description" : "Описание"
    }

    response = await ac.post(
        "/me/to-do-lists",
        json=payload,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_lists_with_pagination(ac: AsyncClient, auth_header: dict, create_many_test_todo_lists):
    """
    Проверка вывода всех листов пользователя с пагинацией.
    """
    await create_many_test_todo_lists(count=3)

    response = await ac.get(
        "/me/to-do-lists",
        headers=auth_header,
        params={"limit" : 2, "offset": 0}
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 2
    assert TypeAdapter(list[ListResponseSchema]).validate_python(data) # проверка листа схем пайдентик


@pytest.mark.parametrize(
    "limit, offset",
    [
        (0, 0),
        (25, 0),
        ("a", "b")
    ]
)
@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_lists_with_incorrect_pagination_params(ac: AsyncClient, auth_header, limit, offset):
    """
    Проверка ошибки указывающей на неверные параметры limit и offset
    """
    response = await ac.get(
        "/me/to-do-lists",
        headers=auth_header,
        params={"limit" : limit, "offset" : offset}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_lists_unauthorized(ac: AsyncClient):
    """
    Проверка ошибки получения листов неавторизированным пользователем.
    """

    response = await ac.get(
        "/me/to-do-lists",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "payload, expected_title, expected_desc",
    [
        ({"title" : "NewTitle", "description":"NewDescription"}, "NewTitle", "NewDescription"),
        ({"title" : "OnlyTitle"}, "OnlyTitle", "Description"),
        ({"description" : "OnlyDescription"}, "Title", "OnlyDescription"),
        ({}, "Title", "Description"),
    ]
)
@pytest.mark.asyncio(loop_scope="session")
async def test_patch_list_success(ac: AsyncClient, auth_header, create_test_todo_list, payload, expected_title, expected_desc):
    """
    Проверка успешного редактирования листа задач по всем параметрам.
    """

    response = await ac.patch(
        f"/me/to-do-lists/{create_test_todo_list.id_list}",
        json=payload,
        headers=auth_header,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    # assert ListResponseSchema.model_validate(data)
    assert data["title"] == expected_title
    assert data["description"] == expected_desc


@pytest.mark.parametrize(
    "bad_payload",
    [
        {"title" : "T" * 33},
        {"description":"D" * 257},
    ]
)
@pytest.mark.asyncio(loop_scope="session")
async def test_patch_list_incorrect_payload(ac: AsyncClient, auth_header, create_test_todo_list, bad_payload):
    """
    Проверка ошибки валидации длины данных.
    """

    response = await ac.patch(
        f"/me/to-do-lists/{create_test_todo_list.id_list}",
        json=bad_payload,
        headers=auth_header,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_list_not_found(ac: AsyncClient, auth_header):
    """
    Проверка ошибки несуществующего листа.
    """
    response = await ac.patch(
        "/me/to-do-lists/99999",
        headers=auth_header,
        json={"title": "any_text"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    data = response.json()
    assert data["detail"] == "List not found"


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_list_unauthorized(ac: AsyncClient):
    """
    Проверка при патче ошибки неавторизированного пользователя.
    """
    response = await ac.patch(
        "/me/to-do-lists/1",
        json={"title": "any_text"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_list_success(ac: AsyncClient, create_test_todo_list, auth_header, session):
    """
    Успешное удаление листа задач.
    """
    existing_list_id = create_test_todo_list.id_list

    response = await ac.delete(
        f"/me/to-do-lists/{existing_list_id}",
        headers=auth_header
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not response.content

    all_lists = await ac.get(
        "/me/to-do-lists",
        headers=auth_header,
        params={"limit" : 20},
    )

    data = all_lists.json()
    all_ids = [lst["id_list"] for lst in data]
    assert existing_list_id not in all_ids


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_list_not_found(ac: AsyncClient, auth_header):
    """
    Проверка при удалении несуществующего листа.
    """
    response = await ac.delete(
        "/me/to-do-lists/99999",
        headers=auth_header
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    data = response.json()
    assert data["detail"] == "List not found"


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_list_unauthorized(ac: AsyncClient):
    """
    Проверка при удалении неавторизированным пользователем.
    """
    response = await ac.delete(
        "/me/to-do-lists/1",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
