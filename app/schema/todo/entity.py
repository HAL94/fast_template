from app.core.database import BaseModelDatabaseMixin
from app.models import Todo as TodoModel, Subtask as SubtaskModel
from typing import ClassVar, Optional
from pydantic import Field

class Todo(BaseModelDatabaseMixin):
    model: ClassVar[type[TodoModel]] = TodoModel

    id: Optional[int] = Field(default=None)
    title: str

    subtasks: Optional[list["Subtask"]] = None

class Subtask(BaseModelDatabaseMixin):
    model: ClassVar[type[SubtaskModel]] = SubtaskModel

    id: Optional[int] = None
    priority: int
    todo_id: Optional[int] = None

