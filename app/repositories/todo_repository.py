from typing import Any, Optional

from app.domain.todo import TodoBase
from app.models import Todo
from app.repositories.base_repository import BaseRepository


class TodoRepository(BaseRepository[TodoBase, Todo]):
    __model__ = Todo

    def domain_model(self, data: dict[Any, Any]) -> TodoBase:
        return TodoBase.model_validate(data, from_attributes=True)

    def model(self):
        return self.__model__
