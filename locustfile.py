import random

from fastapi import status
from locust import HttpUser, between, task


class AppUser(HttpUser):
    wait_time = between(1, 3)  # время ожидания между задачами в секундах

    # первое действие каждого бота перед всем тестом
    def on_start(self):
        """
        Выполняется для каждого отдельного бота при его создании.
        Выполняется один раз при создании бота.
        """
        self.random_num = random.randint(1, 10000)
        self.username = f"username_{self.random_num}"
        self.name = "TestName"
        self.password = "TestPassword"

        reg_payload = {
            "username": self.username,
            "name": self.name,
            "password": self.password,
        }
        self.client.post("/auth/register", json=reg_payload)

        login_data = {"username": self.username, "password": self.password}
        response = self.client.post("/auth/login", data=login_data)

        if response.status_code == status.HTTP_200_OK:
            token = response.json().get("access_token")
            self.client.headers.update({"Authorization": f"Bearer {token}"})

    @task(2)  # вес задачи (как часто вызывать в отношении общего веса всех задач)
    def check_health(self):
        self.client.get("/healthcheck")

    @task(3)
    def user_full_workflow(self):
        """
        Полный изолированный CRUD-цикл работы пользователя.
        Создать лист -> Изменить лист -> Создать задачу -> Изменить задачу ->
        -> Удалить задачу -> Удалить лист.
        """
        # защита от незалогиненных ботов
        if "Authorization" not in self.client.headers:
            return

        # Создать лист
        lst_payload = {"title": "Список задач", "description": "Описание списка задач"}
        response = self.client.post("/me/to-do-lists", json=lst_payload)
        if response.status_code != status.HTTP_201_CREATED:
            return
        existing_id_list = response.json().get("id_list")

        # Изменить лист
        edit_list_payload = {"title": "NewTitle", "description": "NewDescription"}
        response = self.client.patch(
            f"/me/to-do-lists/{existing_id_list}", json=edit_list_payload
        )

        # Создать задачу
        tsk_payload = {"task_name": "Имя задачи", "completed": False}
        response = self.client.post(
            f"/me/to-do-lists/{existing_id_list}/tasks", json=tsk_payload
        )
        if response.status_code != status.HTTP_201_CREATED:
            return
        existing_id_task = response.json().get("id_task")

        # Изменить задачу
        edit_task_payload = {"task_name": "NewName", "completed": True}
        response = self.client.patch(
            f"/me/to-do-lists/{existing_id_list}/tasks/{existing_id_task}",
            json=edit_task_payload,
        )

        # Удалить задачу и лист
        self.client.delete(
            f"/me/to-do-lists/{existing_id_list}/tasks/{existing_id_task}"
        )
        self.client.delete(f"/me/to-do-lists/{existing_id_list}")

    def on_stop(self):
        """
        Выполняется после остановки тестов.
        Гарантирует 100% удаление пользователя, даже если бот не залогинился на старте.
        """
        # Если токен уже есть в заголовках, удалить себя
        if (
            "Authorization" in self.client.headers
            and self.client.headers["Authorization"]
        ):
            self.client.delete("/me/profile")
            return

        # Если токена нет, попытка логиниться еще раз и удалить себя
        login_data = {"username": self.username, "password": self.password}
        response = self.client.post("/auth/login", data=login_data)

        if response.status_code == 200:
            token = response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            # Удаляем профиль, передавая токен точечно в этот конкретный запрос
            self.client.delete("/me/profile", headers=headers)
        else:
            print(f" WARNING: Не удалось зачистить пользователя {self.username}")
