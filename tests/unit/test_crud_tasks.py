import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.crud.tasks import add_task, delete_task, get_all_tasks, patch_task
from src.database.tables import ListsORM, TasksORM, UsersORM
from src.models.schemas import TaskAddSchema, TaskPatchSchema


@pytest.mark.asyncio(loop_scope="session")
async def test_add_task_success(create_test_todo_list: ListsORM):
    existing_list = create_test_todo_list
    task_data = TaskAddSchema(task_name="TaskName")
    new_task = await add_task(
        id_user=existing_list.user_id,
        id_list=existing_list.id_list,
        tsk=task_data
    )

    assert new_task is not None
    assert isinstance(new_task, TasksORM)
    assert new_task.id_task is not None
    assert new_task.list_id == existing_list.id_list
    assert new_task.completed is False # check it out


@pytest.mark.asyncio(loop_scope="session")
async def test_add_task_list_not_found(create_test_user: UsersORM):
    existing_user = create_test_user
    task_data = TaskAddSchema(task_name="TaskName")
    new_task = await add_task(
        id_user=existing_user.id_user,
        id_list=99999,
        tsk=task_data
    )
    assert new_task is None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_tasks_success(session: AsyncSession, create_test_todo_list: ListsORM, create_test_task: TasksORM):
    existing_list = create_test_todo_list
    first_task = create_test_task
    second_task = TasksORM(
        task_name="SecondTask",
        completed=True,
        list_id=first_task.list_id
    )

    session.add(second_task)
    await session.commit()
    await session.refresh(second_task)

    all_tasks = await get_all_tasks(id_user=existing_list.user_id, id_list=existing_list.id_list)

    assert len(all_tasks) > 0
    assert len(all_tasks) == 2
    assert all_tasks[0].id_task is not None
    assert all_tasks[1].id_task is not None
    assert all_tasks[0].list_id == existing_list.id_list
    assert all_tasks[1].list_id == existing_list.id_list


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_tasks_empty_list(create_test_todo_list: ListsORM):
    existing_list = create_test_todo_list

    empty_tasks_list = await get_all_tasks(id_user=existing_list.user_id, id_list=existing_list.id_list)

    assert len(empty_tasks_list) == 0


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_task_success(create_test_todo_list: ListsORM, create_test_task: TasksORM):
    existing_todo_list = create_test_todo_list
    existing_task = create_test_task

    patch_data = TaskPatchSchema(task_name="NewName", completed=True)
    patched_task = await patch_task(
        id_task=existing_task.id_task,
        id_user=existing_todo_list.user_id,
        id_list=existing_task.list_id,
        data=patch_data
    )

    assert patched_task is not None
    assert isinstance(patched_task, TasksORM)
    assert patched_task.task_name == "NewName"
    assert patched_task.completed is True


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_task_partly_success(create_test_todo_list: ListsORM, create_test_task: TasksORM):
    existing_todo_list = create_test_todo_list
    existing_task = create_test_task

    patch_data = TaskPatchSchema(completed=True)
    patched_task = await patch_task(
        id_task=existing_task.id_task,
        id_user=existing_todo_list.user_id,
        id_list=existing_task.list_id,
        data=patch_data
    )

    assert patched_task is not None
    assert isinstance(patched_task, TasksORM)
    assert patched_task.list_id == existing_todo_list.id_list
    assert patched_task.task_name == existing_task.task_name
    assert patched_task.completed is True


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_task_not_found(create_test_todo_list: ListsORM):
    existing_list= create_test_todo_list
    patch_data = TaskPatchSchema(task_name="NewName", completed=True)

    patched_task_not_found = await patch_task(
        id_task=99999,
        id_user=existing_list.user_id,
        id_list=existing_list.id_list,
        data=patch_data
    )

    assert patched_task_not_found is None


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_task_success(create_test_todo_list: ListsORM, create_test_task: TasksORM):
    existing_list = create_test_todo_list
    existing_task = create_test_task

    deleted_task = await delete_task(
        id_task=existing_task.id_task,
        id_user=existing_list.user_id,
        id_list=existing_task.list_id,
    )

    assert deleted_task is True


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_task_not_found(create_test_todo_list: ListsORM, create_test_task: TasksORM):
    existing_list = create_test_todo_list
    existing_task = create_test_task

    deleted_task = await delete_task(
        id_task=99999,
        id_user=existing_list.user_id,
        id_list=existing_task.list_id
    )

    assert deleted_task is False


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_tasks_sorted_pagination_success(create_test_todo_list: ListsORM, create_many_test_tasks):
    """
    Проверка пагинации.
    Создает две страницы с разным количеством элементов.
    Проверяется соответствие количества элементов на каждой странице.
    Проверяется уникальность айди задач на обоих страницах.
    """
    existing_list = create_test_todo_list
    await create_many_test_tasks(count=9)

    page_1 = await get_all_tasks(id_user=existing_list.user_id, id_list=existing_list.id_list, limit=5, offset=0)
    page_2 = await get_all_tasks(id_user=existing_list.user_id, id_list=existing_list.id_list, limit=5, offset=5)

    assert len(page_1) == 5
    assert len(page_2) == 4

    tasks_ids = [tsk.id_task for tsk in page_1] + [tsk.id_task for tsk in page_2]

    assert len(tasks_ids) == len(set(tasks_ids))
    assert tasks_ids == sorted(tasks_ids)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_tasks_pagination_empty_page(create_test_todo_list: ListsORM, create_many_test_tasks):
    """
    Проверка если offset больше количества записей. Возвращается пустой список.
    """
    existing_list = create_test_todo_list
    await create_many_test_tasks(count=9)

    empty_page = await get_all_tasks(id_user=existing_list.user_id, id_list=existing_list.id_list, limit=5, offset=10)

    assert empty_page == []


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_tasks_pagination_with_single_page(create_test_todo_list: ListsORM, create_many_test_tasks):
    """
    Проверка если limit больше количества записей, возвращается правильное количество записей (без заглушек).
    """
    existing_list = create_test_todo_list
    await create_many_test_tasks(count=4)

    single_page = await get_all_tasks(id_user=existing_list.user_id, id_list=existing_list.id_list, limit=10, offset=0)

    assert len(single_page) == 4
