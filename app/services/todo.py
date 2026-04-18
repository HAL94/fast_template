from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginatedResult
from app.domain.todo import SubtaskBase, TodoBase, TodoWithTasks
from app.dto.todo import TodoCreate
from app.repositories.subtask_repository import SubtaskRepository
from app.repositories.todo_repository import TodoRepository
from app.services.base import BaseService


class TodoService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.todo_repo = TodoRepository(session=session)
        self.subtask_repo = SubtaskRepository(session=session)

    async def get_todos(self) -> PaginatedResult[TodoBase]:
        return await self.todo_repo.get_many()

    async def get_todo(self, todo_id: UUID) -> TodoWithTasks:
        where_clause = [TodoBase.model.id == todo_id]
        return await self.todo_repo.get_one(where_clause, options=TodoWithTasks.relations(), domain_model=TodoWithTasks)

    async def create_todo(self, todo_create: TodoCreate) -> TodoWithTasks:
        created_todo = await self.todo_repo.create_one(TodoBase(title=todo_create.title))
        subtask_payload: list[SubtaskBase] = []

        for subtask in todo_create.subtasks:
            subtask_payload.append(SubtaskBase(todo_id=created_todo.id, title=subtask.title, priority=subtask.priority))

        created_subtasks = await self.subtask_repo.create_many(subtask_payload)

        await self.session.commit()

        todo = TodoWithTasks.model_validate(created_todo, from_attributes=True)
        todo.subtasks = created_subtasks
        return todo

    async def delete_todo(self, todo_id: UUID) -> Optional[TodoWithTasks]:
        where_clause = [TodoBase.model.id == todo_id]

        todo_to_delete = await self.todo_repo.get_one_or_none(
            where_clause, options=TodoWithTasks.relations(), domain_model=TodoWithTasks
        )
        if not todo_to_delete:
            return None

        await self.todo_repo.delete(where_clause)

        await self.session.commit()

        return todo_to_delete
