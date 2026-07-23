# import pytest
# from httpx import AsyncClient


# @pytest.mark.asyncio
# async def test_register_user(client: AsyncClient):
#     register_data = {
#         "name" : "test name",
#         "email" : "test_user@example.com",
#         "password" : "test_secret_password"
#     }

#     response = await client.post("/register", json=register_data)
#     assert response.status_code == 201
#     response_json = response.json()

#     from src.auth.schemas import UserReadSchema

#     user_schema = UserReadSchema.model_validate(response_json)

#     assert user_schema.name == register_data["name"]
#     assert user_schema.email == register_data["email"]
#     assert user_schema.id_user is not None
#     assert isinstance(user_schema.id_user, int)
