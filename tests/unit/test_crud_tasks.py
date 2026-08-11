import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.crud.tasks import add_task, delete_task, get_all_tasks, patch_task
from src.database.tables import ListsORM, TasksORM, UsersORM
from src.models.schemas import TaskAddSchema, TaskPatchSchema


@pytest.mark.asyncio(loop_scope="session")
async def test_add_task_success(create_test_todo_list: ListsORM):
    existed_list = create_test_todo_list
    task_data = TaskAddSchema(task_name="TaskName")
    new_task = await add_task(
        id_user=existed_list.user_id,
        id_list=existed_list.id_list,
        tsk=task_data
    )

    assert new_task is not None
    assert isinstance(new_task, TasksORM)
    assert new_task.id_task is not None
    assert new_task.list_id == existed_list.id_list
    assert new_task.completed is False # check it out

@pytest.mark.asyncio(loop_scope="session")
async def test_add_task_list_not_found(create_test_user: UsersORM):
    existed_user = create_test_user
    task_data = TaskAddSchema(task_name="TaskName")
    new_task = await add_task(
        id_user=existed_user.id_user,
        id_list=99999,
        tsk=task_data
    )
    assert new_task is None

@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_tasks_success(session: AsyncSession, create_test_todo_list: ListsORM, create_test_task: TasksORM):
    existed_list = create_test_todo_list
    first_task = create_test_task
    second_task = TasksORM(
        task_name="SecondTask",
        completed=True,
        list_id=first_task.list_id
    )

    session.add(second_task)
    await session.commit()
    await session.refresh(second_task)

    all_tasks = await get_all_tasks(id_user=existed_list.user_id, id_list=existed_list.id_list)

    assert len(all_tasks) > 0
    assert len(all_tasks) == 2
    assert all_tasks[0].id_task is not None
    assert all_tasks[1].id_task is not None
    assert all_tasks[0].list_id == existed_list.id_list
    assert all_tasks[1].list_id == existed_list.id_list

@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_tasks_empty_list(create_test_todo_list: ListsORM):
    existed_list = create_test_todo_list

    empty_tasks_list = await get_all_tasks(id_user=existed_list.user_id, id_list=existed_list.id_list)

    assert len(empty_tasks_list) == 0

@pytest.mark.asyncio(loop_scope="session")
async def test_patch_task_success(create_test_todo_list: ListsORM, create_test_task: TasksORM):
    existed_todo_list = create_test_todo_list
    existed_task = create_test_task

    patch_data = TaskPatchSchema(task_name="NewName", completed=True)
    patched_task = await patch_task(
        id_task=existed_task.id_task,
        id_user=existed_todo_list.user_id,
        id_list=existed_task.list_id,
        data=patch_data
    )

    assert patched_task is not None
    assert isinstance(patched_task, TasksORM)
    assert patched_task.task_name == "NewName"
    assert patched_task.completed is True

@pytest.mark.asyncio(loop_scope="session")
async def test_patch_task_partly_success(create_test_todo_list: ListsORM, create_test_task: TasksORM):
    existed_todo_list = create_test_todo_list
    existed_task = create_test_task

    patch_data = TaskPatchSchema(completed=True)
    patched_task = await patch_task(
        id_task=existed_task.id_task,
        id_user=existed_todo_list.user_id,
        id_list=existed_task.list_id,
        data=patch_data
    )

    assert patched_task is not None
    assert isinstance(patched_task, TasksORM)
    assert patched_task.list_id == existed_todo_list.id_list
    assert patched_task.task_name == existed_task.task_name
    assert patched_task.completed is True

@pytest.mark.asyncio(loop_scope="session")
async def test_patch_task_not_found(create_test_todo_list: ListsORM):
    existed_list= create_test_todo_list
    patch_data = TaskPatchSchema(task_name="NewName", completed=True)

    patched_task_not_found = await patch_task(
        id_task=99999,
        id_user=existed_list.user_id,
        id_list=existed_list.id_list,
        data=patch_data
    )

    assert patched_task_not_found is None

@pytest.mark.asyncio(loop_scope="session")
async def test_delete_task_success(create_test_todo_list: ListsORM, create_test_task: TasksORM):
    existed_list = create_test_todo_list
    existed_task = create_test_task

    deleted_task = await delete_task(
        id_task=existed_task.id_task,
        id_user=existed_list.user_id,
        id_list=existed_task.list_id,
    )

    assert deleted_task is True

@pytest.mark.asyncio(loop_scope="session")
async def test_delete_task_not_found(create_test_todo_list: ListsORM, create_test_task: TasksORM):
    existed_list = create_test_todo_list
    existed_task = create_test_task

    deleted_task = await delete_task(
        id_task=99999,
        id_user=existed_list.user_id,
        id_list=existed_task.list_id
    )

    assert deleted_task is False
