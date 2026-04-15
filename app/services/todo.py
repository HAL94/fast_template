from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.todo import SubtaskBase, TodoBase, TodoWithTasks
from app.dto.todo import TodoCreate
from app.models import Subtask, Todo
from app.repositories.todo_repository import TodoRepository
from app.services.base import BaseService


class TodoService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self._todo = TodoBase
        self._todo_with_tasks = TodoWithTasks
        self._subtasks = SubtaskBase
        self.repo = TodoRepository(session=session)

    def _get_model(self) -> type[TodoBase]:
        return self._todo

    async def get_todos(self) -> list[TodoWithTasks]:
        return await self._todo_with_tasks.get_all(self.session)

    async def get_todo(self, todo_id: int) -> TodoBase:
        # return await self._todo_with_tasks.get_one(self.session, todo_id)
        result_exists = await self.repo.exists([self.repo.model().id == todo_id])
        print(f"Todo exists with id {todo_id}: {result_exists}")
        return await self.repo.get_one([self.repo.model().id == todo_id])

    async def create_todo(self, todo_create: TodoCreate) -> TodoBase:
        result = await self.repo.create(todo_create)
        await self.session.commit()
        return self.repo.domain_model(result)
        # todo: Todo = await self._todo.create(
        #     self.session,
        #     TodoBase(title=todo_create.title),
        #     commit=False,
        #     return_as_base=True,
        # )
        # todo.subtasks = [
        #     Subtask(task=todo, priority=subtask.priority, title=subtask.title) for subtask in todo_create.subtasks
        # ]
        # await self.session.commit()
        # return TodoWithTasks.model_validate({"title": todo.title, "subtasks": todo.subtasks, "id": todo.id})
