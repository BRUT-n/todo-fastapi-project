import pytest
from src.database.crud.users import delete_user, patch_user
from src.database.tables import UsersORM
from src.models.schemas import UserPatchSchema


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_user_name_success(create_test_user):
    new_user = create_test_user

    patch_data = UserPatchSchema(name="NewUserName")
    updated_user = await patch_user(user_id=new_user.id_user, data=patch_data)

    assert updated_user is not None
    assert isinstance(updated_user, UsersORM)
    assert updated_user.name == "NewUserName"
    assert updated_user.email == "usermail@test.com"

@pytest.mark.asyncio(loop_scope="session")
async def test_patch_user_email_success(create_test_user):
    new_user = create_test_user

    patch_data = UserPatchSchema(email="newemail@test.com")
    updated_user = await patch_user(user_id=new_user.id_user, data=patch_data)

    assert updated_user is not None
    assert isinstance(updated_user, UsersORM)
    assert updated_user.name == new_user.name
    assert updated_user.email == "newemail@test.com"

@pytest.mark.asyncio(loop_scope="session")
async def test_patch_user_email__already_exists(session, create_test_user):

    second_user = UsersORM(
        name="Name2",
        email="name2mail@test.com",
        hashed_password=b"secret_password1"
    )

    session.add(second_user)
    await session.commit()
    await session.refresh(second_user)

    patch_data = UserPatchSchema(email="usermail@test.com")
    updated_user = await patch_user(user_id=second_user.id_user, data=patch_data)

    assert updated_user is False

@pytest.mark.asyncio(loop_scope="session")
async def test_patch_user_not_found(session):
    patch_data = UserPatchSchema(name="Name", email="testmail@test.com")
    result = await patch_user(user_id=99, data=patch_data)

    assert result is None

@pytest.mark.asyncio(loop_scope="session")
async def test_delete_user(create_test_user):
    user = create_test_user
    deleted_user = await delete_user(user_id=user.id_user)

    assert deleted_user is True

@pytest.mark.asyncio(loop_scope="session")
async def test_delete_user_not_found():
    deleted_user = await delete_user(user_id=99)

    assert deleted_user is None
