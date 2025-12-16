from typing import ClassVar, Optional

from pydantic import Field
from sqlalchemy.orm import selectinload

from app.core.database import BaseModelDatabaseMixin
from app.models import Subtask as SubtaskModel
from app.models import Todo as TodoModel


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
