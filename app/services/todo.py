from typing import ClassVar
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.todo import TodoBase, TodoWithTasks, SubtaskBase
from app.dto.todo import TodoCreate
from app.models import Subtask, Todo


class TodoService:
    _todo: ClassVar[TodoBase] = TodoBase
    _todo_with_tasks: ClassVar[TodoWithTasks] = TodoWithTasks
    _subtasks: ClassVar[SubtaskBase] = SubtaskBase

    @classmethod
    async def get_todo(cls, session: AsyncSession, todo_id: int) -> TodoBase:
        return await cls._todo_with_tasks.get_one(session, todo_id)

    @classmethod
    async def create_todo(
        cls, session: AsyncSession, todo_create: TodoCreate
    ) -> TodoWithTasks:
        todo: Todo = await cls._todo.create(
            session,
            TodoBase(title=todo_create.title),
            commit=False,
            return_as_base=True,
        )
        todo.subtasks = [
            Subtask(task=todo, priority=subtask.priority)
            for subtask in todo_create.subtasks
        ]
        await session.commit()
        return TodoWithTasks.model_validate(
            {"title": todo.title, "subtasks": todo.subtasks, "id": todo.id}
        )
