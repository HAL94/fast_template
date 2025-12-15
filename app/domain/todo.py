from app.core.database import BaseModelDatabaseMixin
from app.models import Todo as TodoModel, Subtask as SubtaskModel
from sqlalchemy.orm import selectinload
from typing import ClassVar, Optional
from pydantic import Field


class TodoBase(BaseModelDatabaseMixin):
    model: ClassVar[type[TodoModel]] = TodoModel

    @classmethod
    def relations(cls):
        return [selectinload(cls.model.subtasks)]

    id: Optional[int] = Field(default=None)
    title: str


class TodoWithTasks(TodoBase):
    subtasks: Optional[list["SubtaskBase"]] = Field(default=[])


class SubtaskBase(BaseModelDatabaseMixin):
    model: ClassVar[type[SubtaskModel]] = SubtaskModel

    id: Optional[int] = None
    priority: int
    todo_id: Optional[int] = None
