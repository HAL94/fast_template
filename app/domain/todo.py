from typing import ClassVar, Optional
from uuid import UUID

from pydantic import Field
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.strategy_options import _AbstractLoad

from app.domain.base import BaseDomain
from app.models import Subtask, Todo


class TodoBase(BaseDomain[Todo]):
    model: ClassVar[Todo] = Todo

    id: Optional[UUID] = Field(default=None)
    title: str
    user_id: UUID


class TodoWithTasks(TodoBase):
    @classmethod
    def relations(cls) -> list[_AbstractLoad]:
        return [selectinload(Todo.subtasks)]

    subtasks: Optional[list["SubtaskBase"]] = Field(default=[])


class SubtaskBase(BaseDomain[Subtask]):
    model: ClassVar[Subtask] = Subtask
    id: Optional[UUID] = None
    todo_id: UUID
    title: Optional[str] = None
    priority: Optional[int] = None
