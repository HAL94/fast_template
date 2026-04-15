from typing import ClassVar, Optional

from pydantic import Field

from app.core.schema import BaseModel


class TodoBase(BaseModel):
    id: Optional[int] = Field(default=None)
    title: str
    # subtasks: Optional[list["SubtaskBase"]] = Field(default=[])


class TodoWithTasks(TodoBase):
    subtasks: Optional[list["SubtaskBase"]] = Field(default=[])


class SubtaskBase(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    priority: int
