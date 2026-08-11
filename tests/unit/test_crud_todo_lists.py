import pytest
from src.database.crud.todo_lists import (
    add_todo_lists,
    delete_list,
    get_lists,
    patch_list,
)
from src.database.tables import ListsORM, UsersORM
from src.models.schemas import ListAddSchema, ListPatchSchema

title_data = "ListTitle"
description_data = "ListDescription"

@pytest.mark.asyncio(loop_scope="session")
async def test_add_todo_list_success(create_test_user: UsersORM):
    existed_user = create_test_user
    list_to_create = ListAddSchema(title=title_data, description=description_data)
    new_list = await add_todo_lists(id_user=existed_user.id_user, lst=list_to_create)

    assert new_list is not None
    assert isinstance(new_list, ListsORM)
    assert new_list.id_list is not None
    assert new_list.user_id == existed_user.id_user

@pytest.mark.asyncio(loop_scope="session")
async def test_add_todo_list_user_not_found():
    list_to_create = ListAddSchema(title=title_data, description=description_data)
    new_list = await add_todo_lists(id_user=99999, lst=list_to_create)

    assert new_list is None

@pytest.mark.asyncio(loop_scope="session")
async def test_get_lists_success(create_test_todo_list: ListsORM):
    existed_list = create_test_todo_list
    lists_to_get = await get_lists(id_user=existed_list.user_id)

    assert len(lists_to_get) == 1
    assert lists_to_get[0].user_id == existed_list.user_id

@pytest.mark.asyncio(loop_scope="session")
async def test_get_lists_empty(create_test_user: UsersORM):
    existed_user = create_test_user
    lists_to_get = await get_lists(id_user=existed_user.id_user)

    assert isinstance(lists_to_get, list)
    assert len(lists_to_get) == 0

@pytest.mark.asyncio(loop_scope="session")
async def test_patch_list_title_success(create_test_todo_list: ListsORM):
    existed_list = create_test_todo_list
    old_description = existed_list.description
    patch_data = ListPatchSchema(title=title_data)

    patched_list = await patch_list(
        id_user=existed_list.user_id,
        id_list=existed_list.id_list,
        data=patch_data
    )

    assert patched_list is not None
    assert isinstance(patched_list, ListsORM)
    assert patched_list.title == title_data
    assert patched_list.description == old_description

@pytest.mark.asyncio(loop_scope="session")
async def test_patch_list_all_fields_success(create_test_todo_list: ListsORM):
    existed_list = create_test_todo_list
    patch_data = ListPatchSchema(title=title_data, description=description_data)

    patched_lits = await patch_list(
        id_user=existed_list.user_id,
        id_list=existed_list.id_list,
        data=patch_data
    )

    assert patched_lits is not None
    assert isinstance(patched_lits, ListsORM)
    assert patched_lits.title == title_data
    assert patched_lits.description == description_data

@pytest.mark.asyncio(loop_scope="session")
async def test_patch_list_not_found(create_test_user: UsersORM):
    existed_user = create_test_user
    patch_data = ListPatchSchema(title=title_data, description=description_data)

    patched_list = await patch_list(
        id_user=existed_user.id_user,
        id_list=99999,
        data=patch_data
    )

    assert patched_list is None

@pytest.mark.asyncio(loop_scope="session")
async def test_delete_list_success(create_test_todo_list: ListsORM):
    existed_list = create_test_todo_list

    deleted_list = await delete_list(
        id_user=existed_list.user_id,
        id_list=existed_list.id_list
    )

    assert deleted_list is True

@pytest.mark.asyncio(loop_scope="session")
async def test_delete_list_not_found(create_test_user: UsersORM):
    existed_user = create_test_user
    deleted_list = await delete_list(
        id_user=existed_user.id_user,
        id_list=99999
    )

    assert deleted_list is False
