import httpx
import pytest
from fastapi import status


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_full_lifecycle_success(ac_online: httpx.AsyncClient):
    """
    Полный цикл работы приложения.
    Регистрация - логин - создание листа - создание задачи
     - отметка выполнения задачи - патч листа - патч задачи - удаление листа - удаление пользователя.
    """
    # регистрация пользователя
    reg_payload = {
        "username" : "e2e_username",
        "name" : "Name",
        "password" : "secret_password"
    }

    reg_response = await ac_online.post(
        "/auth/register",
        json=reg_payload
    )

    assert reg_response.status_code == status.HTTP_201_CREATED

    # логин пользователя с получением токена
    login_payload = {
        "username" : reg_payload["username"],
        "password" : reg_payload["password"]
    }

    login_response = await ac_online.post(
        "/auth/login",
        data=login_payload
    )

    assert login_response.status_code == status.HTTP_200_OK

    token = login_response.json()["access_token"]
    auth_e2e_header = {"Authorization" : f"Bearer {token}"}

    try:
        # получение личных данных
        get_me_response = await ac_online.get(
            "/auth/me",
            headers=auth_e2e_header
        )

        assert get_me_response.status_code == status.HTTP_200_OK

        # изменение данных пользователя
        patch_user_payload = {
            "username" : "e2e_new_username",
            "name" : "NewName",
            "email" : "testmail@e2e.com"
        }

        patch_user_response = await ac_online.patch(
            "/me/profile",
            json=patch_user_payload,
            headers=auth_e2e_header
        )

        assert patch_user_response.status_code == status.HTTP_200_OK

        # # создание нового листа
        # todo_list_payload = {
        #     "title" : "Список продуктов",
        #     "description" : "Стол на корпоратив"
        # }

        # todo_list_response = await ac_online.post(
        #     "/me/to-do-lists",
        #     json=todo_list_payload,
        #     headers=auth_e2e_header
        # )

        # assert todo_list_response.status_code == status.HTTP_201_CREATED

        # existing_todo_list = todo_list_response.json()

        # создание нескольких листов для пагинации
        created_many_lists = []
        num_of_lists = 6

        for i in range(1, num_of_lists + 1):
            many_lists_payload = {
            "title" : f"Список №{i}",
            "description" : f"Описание списка №{i}"
            }

            todo_list_in_many_response = await ac_online.post(
                "/me/to-do-lists",
                json=many_lists_payload,
                headers=auth_e2e_header
            )
            created_many_lists.append(todo_list_in_many_response.json())

        # проверка пагинации
        get_lists_page_1_response = await ac_online.get(
            "/me/to-do-lists",
            headers=auth_e2e_header,
            params={"limit" : 5, "offset": 0}
        )

        assert get_lists_page_1_response.status_code == status.HTTP_200_OK

        page_1 = get_lists_page_1_response.json()
        assert len(page_1) == 5

        get_lists_page_2_response = await ac_online.get(
            "/me/to-do-lists",
            headers=auth_e2e_header,
            params={"limit" : 5, "offset": 5}
        )

        assert get_lists_page_2_response.status_code == status.HTTP_200_OK

        page_2 = get_lists_page_2_response.json()
        assert len(page_2) == 1 # в зависимости от кол-ва созданных

        # изменение данных листа
        existing_list_id = created_many_lists[0]["id_list"]

        patch_list_payload = {
            "title" : "NewTitle",
            "description":"NewDescription"
        }

        patch_list_response = await ac_online.patch(
            f"/me/to-do-lists/{existing_list_id}",
            json=patch_list_payload,
            headers=auth_e2e_header
        )

        assert patch_list_response.status_code == status.HTTP_200_OK

    finally:
            response = await ac_online.delete(
            "/me/profile",
            headers=auth_e2e_header
            )

            assert response.status_code == status.HTTP_204_NO_CONTENT


# TODO: test_delete_user (e2e_new_username конечное, учитывать при удалении)
# TODO: реализорвать очистку БД если тесты упадут
