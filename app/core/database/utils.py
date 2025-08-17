from typing import TYPE_CHECKING, Any
from .base import Base
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from .validation import is_pydantic_database_mixin

if TYPE_CHECKING:
    from .mixin import BaseModelDatabaseMixin


class CreateModelRelations:
    def __init__(self, model: type[Base], pydantic: "BaseModelDatabaseMixin"):
        self.model = model
        self.pydantic = pydantic

    async def create_with_relations(
        self,
        session: AsyncSession,
        data: BaseModel,
        /,
        *,
        commit: bool = False,
    ):
        relationships = self.model.get_relationships()
        parsed = dict(data)

        direct_fields = {}
        relation_data = {}

        for key, value in parsed.items():
            if key in relationships:
                relation_data[key] = value
            else:
                direct_fields[key] = value

        obj = await self.model.create(session, direct_fields, commit=commit)

        for rel_key, rel_value in parsed.items():
            if rel_key in relationships:
                await self._handle_relation(session, obj, rel_key, rel_value, commit)

        # print(f"Created with or without relaitons: {obj}")
        return obj

    async def _handle_relation(
        self,
        session: AsyncSession,
        parent_obj: Base,
        rel_key: str,
        rel_value: Any,
        commit: bool,
    ):
        """Handle a specific relationship"""

        # Determine the related Pydantic class
        if rel_value and is_pydantic_database_mixin(rel_value):
            # print(f"Handling single relation: {rel_value}")
            await self._handle_single_relation(
                session, parent_obj, rel_key, rel_value, commit
            )
        elif rel_value and isinstance(rel_value, list) and len(rel_value) > 0:
            # print(f"Handling list relation: {rel_value}")
            await self._handle_list_relations(
                session, parent_obj, rel_key, rel_value, commit
            )

        return parent_obj

    @classmethod
    async def _handle_single_relation(
        self,
        session: AsyncSession,
        parent_obj,
        rel_key: str,
        rel_value: "BaseModelDatabaseMixin",
        commit: bool,
    ):
        handler = CreateModelRelations(model=rel_value.model, pydantic=rel_value)
        if rel_value is not None:
            child_data: Base = await handler.create_with_relations(
                session, rel_value, commit=commit
            )
            setattr(parent_obj, rel_key, child_data)

    async def _handle_list_relations(
        self,
        session: AsyncSession,
        parent_obj: Base,
        rel_key: str,
        rel_value: list[Any],
        commit: bool,
    ):
        sub_data_result = []
        for item in rel_value:
            if not item or not is_pydantic_database_mixin(item):
                raise ValueError("data is None or not of type BaseModelDatabaseMixin")
            handler = CreateModelRelations(model=item.model, pydantic=item)
            item_result: Base = await handler.create_with_relations(
                session, item, commit=commit
            )
            sub_data_result.append(item_result)

        setattr(parent_obj, rel_key, sub_data_result)
