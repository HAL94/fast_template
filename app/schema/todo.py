from app.core.database import BaseModelDatabaseMixin
from app.models import Todo as TodoModel
from typing import ClassVar, Optional
from pydantic import Field

class Todo(BaseModelDatabaseMixin):
    model: ClassVar[type[TodoModel]] = TodoModel

    id: Optional[int] = Field(default=None)
    title: str
