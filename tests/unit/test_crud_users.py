import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.crud.users import delete_user, patch_user
from src.database.tables import UsersORM
from src.models.schemas import UserPatchSchema

USERNAME_DATA ="NewUniqueUsername"
NAME_DATA = "NewUserName"
EMAIL_DATA = "newemail@test.com"


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_user_username_success(create_test_user):
    existing_user = create_test_user
    name = existing_user.name

    patch_data = UserPatchSchema(username=USERNAME_DATA)
    updated_user = await patch_user(user_id=existing_user.id_user, data=patch_data)

    assert updated_user is not None
    assert isinstance(updated_user, UsersORM)
    assert updated_user.username == USERNAME_DATA
    assert updated_user.name == name


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_user_name_success(create_test_user: UsersORM):
    existing_user = create_test_user
    old_email = existing_user.email

    patch_data = UserPatchSchema(name=NAME_DATA)
    updated_user = await patch_user(user_id=existing_user.id_user, data=patch_data)

    assert updated_user is not None
    assert isinstance(updated_user, UsersORM)
    assert updated_user.name == NAME_DATA
    assert updated_user.email == old_email


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_user_email_success(create_test_user: UsersORM):
    existing_user = create_test_user
    old_name = existing_user.name

    patch_data = UserPatchSchema(email=EMAIL_DATA)
    updated_user = await patch_user(user_id=existing_user.id_user, data=patch_data)

    assert updated_user is not None
    assert isinstance(updated_user, UsersORM)
    assert updated_user.name == old_name
    assert updated_user.email == EMAIL_DATA


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_user_not_found():
    patch_data = UserPatchSchema(username=USERNAME_DATA, name=NAME_DATA, email=EMAIL_DATA)
    result = await patch_user(user_id=99999, data=patch_data)

    assert result is None


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_user_success(session: AsyncSession, create_test_user: UsersORM):
    user = create_test_user
    await delete_user(user_id=user.id_user)

    check_query = select(UsersORM).where(UsersORM.id_user == user.id_user)
    result = await session.execute(check_query)
    deleted_user = result.scalar_one_or_none()

    assert deleted_user is None


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_user_not_found():
    result = await delete_user(user_id=99999)

    assert result is None
