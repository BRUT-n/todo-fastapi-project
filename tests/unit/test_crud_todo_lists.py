import pytest
from src.database.crud.todo_lists import (
    add_todo_lists,
    delete_list,
    get_lists,
    patch_list,
)
from src.database.tables import ListsORM, UsersORM
from src.models.schemas import ListAddSchema, ListPatchSchema

TITLE_DATA = "ListTitle"
DESCRIPTION_DATA = "ListDescription"


@pytest.mark.asyncio(loop_scope="session")
async def test_add_todo_list_success(create_test_user: UsersORM):
    existing_user = create_test_user
    list_to_create = ListAddSchema(title=TITLE_DATA, description=DESCRIPTION_DATA)
    new_list = await add_todo_lists(id_user=existing_user.id_user, lst=list_to_create)

    assert new_list is not None
    assert isinstance(new_list, ListsORM)
    assert new_list.id_list is not None
    assert new_list.user_id == existing_user.id_user


@pytest.mark.asyncio(loop_scope="session")
async def test_get_lists_success(create_test_todo_list: ListsORM):
    existing_list = create_test_todo_list
    lists_to_get = await get_lists(id_user=existing_list.user_id)

    assert len(lists_to_get) == 1
    assert lists_to_get[0].user_id == existing_list.user_id


@pytest.mark.asyncio(loop_scope="session")
async def test_get_lists_empty(create_test_user: UsersORM):
    existing_user = create_test_user
    lists_to_get = await get_lists(id_user=existing_user.id_user)

    assert isinstance(lists_to_get, list)
    assert len(lists_to_get) == 0


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_list_title_success(create_test_todo_list: ListsORM):
    existing_list = create_test_todo_list
    old_description = existing_list.description
    patch_data = ListPatchSchema(title=TITLE_DATA)

    patched_list = await patch_list(
        id_user=existing_list.user_id, id_list=existing_list.id_list, data=patch_data
    )

    assert patched_list is not None
    assert isinstance(patched_list, ListsORM)
    assert patched_list.title == TITLE_DATA
    assert patched_list.description == old_description


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_list_all_fields_success(create_test_todo_list: ListsORM):
    existing_list = create_test_todo_list
    patch_data = ListPatchSchema(title=TITLE_DATA, description=DESCRIPTION_DATA)

    patched_lits = await patch_list(
        id_user=existing_list.user_id, id_list=existing_list.id_list, data=patch_data
    )

    assert patched_lits is not None
    assert isinstance(patched_lits, ListsORM)
    assert patched_lits.title == TITLE_DATA
    assert patched_lits.description == DESCRIPTION_DATA


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_list_not_found(create_test_user: UsersORM):
    existing_user = create_test_user
    patch_data = ListPatchSchema(title=TITLE_DATA, description=DESCRIPTION_DATA)

    patched_list = await patch_list(
        id_user=existing_user.id_user, id_list=99999, data=patch_data
    )

    assert patched_list is None


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_list_success(create_test_todo_list: ListsORM):
    existing_list = create_test_todo_list

    deleted_list = await delete_list(
        id_user=existing_list.user_id, id_list=existing_list.id_list
    )

    assert deleted_list is True


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_list_not_found(create_test_user: UsersORM):
    existing_user = create_test_user
    deleted_list = await delete_list(id_user=existing_user.id_user, id_list=99999)

    assert deleted_list is False


@pytest.mark.asyncio(loop_scope="session")
async def test_get_lists_sorted_pagination_success(
    create_test_user: UsersORM, create_many_test_todo_lists
):
    """
    Проверка пагинации.
    Создает две страницы с разным количеством элементов.
    Проверяется соответствие количества элементов на каждой странице.
    Проверяется уникальность айди листов на обоих страницах.
    Проверяется сортировка по айди.
    """
    existing_user = create_test_user
    await create_many_test_todo_lists()

    page_1 = await get_lists(id_user=existing_user.id_user, limit=5, offset=0)
    page_2 = await get_lists(id_user=existing_user.id_user, limit=5, offset=5)

    assert len(page_1) == 5
    assert len(page_2) == 3

    list_ids = [lst.id_list for lst in page_1] + [lst.id_list for lst in page_2]

    assert len(list_ids) == len(set(list_ids))
    assert list_ids == sorted(list_ids)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_lists_pagination_empty_page(
    create_test_user: UsersORM, create_many_test_todo_lists
):
    """
    Проверка если offset больше количества записей. Возвращается пустой список.
    """
    existing_user = create_test_user
    await create_many_test_todo_lists()

    empty_page = await get_lists(id_user=existing_user.id_user, limit=5, offset=10)

    assert empty_page == []


@pytest.mark.asyncio(loop_scope="session")
async def test_get_lists_pagination_with_single_page(
    create_test_user: UsersORM, create_many_test_todo_lists
):
    """
    Проверка если limit больше количества записей, возвращается
    правильное количество записей (без заглушек).
    """
    existing_user = create_test_user
    await create_many_test_todo_lists(count=3)

    single_page = await get_lists(id_user=existing_user.id_user, limit=10, offset=0)

    assert len(single_page) == 3
