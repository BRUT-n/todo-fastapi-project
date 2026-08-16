import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.crud.users import delete_user, patch_user
from src.database.tables import UsersORM
from src.models.schemas import UserPatchSchema

NAME_DATA = "NewUserName"
EMAIL_DATA = "newemail@test.com"

@pytest.mark.asyncio(loop_scope="session")
async def test_patch_user_name_success(create_test_user: UsersORM):
    existed_user = create_test_user
    old_email = existed_user.email

    patch_data = UserPatchSchema(name=NAME_DATA)
    updated_user = await patch_user(user_id=existed_user.id_user, data=patch_data)

    assert updated_user is not None
    assert isinstance(updated_user, UsersORM)
    assert updated_user.name == NAME_DATA
    assert updated_user.email == old_email

@pytest.mark.asyncio(loop_scope="session")
async def test_patch_user_email_success(create_test_user: UsersORM):
    existed_user = create_test_user
    old_name = existed_user.name

    patch_data = UserPatchSchema(email=EMAIL_DATA)
    updated_user = await patch_user(user_id=existed_user.id_user, data=patch_data)

    assert updated_user is not None
    assert isinstance(updated_user, UsersORM)
    assert updated_user.name == old_name
    assert updated_user.email == EMAIL_DATA

# TODO переписать исходные функции и используя миграцию алембик

# @pytest.mark.asyncio(loop_scope="session")
# async def test_patch_user_email_already_exists(session: AsyncSession, create_test_user: UsersORM):

#     second_user = UsersORM(
#         name="Name2",
#         email="name2mail@test.com",
#         hashed_password=b"secret_password2"
#     )

#     session.add(second_user)
#     await session.commit()
#     await session.refresh(second_user)

#     patch_data = UserPatchSchema(email="mail_to_patch")
#     updated_user = await patch_user(user_id=second_user.id_user, data=patch_data)

#     assert updated_user is False

@pytest.mark.asyncio(loop_scope="session")
async def test_patch_user_not_found():
    patch_data = UserPatchSchema(name=NAME_DATA, email=EMAIL_DATA)
    result = await patch_user(user_id=99999, data=patch_data)

    assert result is None

@pytest.mark.asyncio(loop_scope="session")
async def test_delete_user(session: AsyncSession, create_test_user: UsersORM):
    user = create_test_user
    await delete_user(user_id=user.id_user)

    check_query = select(UsersORM).where(UsersORM.id_user == user.id_user)
    result = await session.execute(check_query)
    deleted_user = result.scalar_one_or_none()

    assert deleted_user is None
