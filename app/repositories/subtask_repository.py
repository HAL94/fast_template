from typing import Any, Optional

from app.domain.base import BaseDomain
from app.domain.todo import SubtaskBase
from app.models import Subtask
from app.repositories.base_repository import BaseRepository


class SubtaskRepository(BaseRepository[SubtaskBase, Subtask]):
    __model__ = Subtask

    def domain_model(self, data: dict[str, Any], as_domain: Optional[BaseDomain] = None) -> SubtaskBase:
        if as_domain:
            return as_domain.model_validate(data, from_attributes=True)
        return SubtaskBase.model_validate(data, from_attributes=True)

    def model(self):
        return self.__model__
