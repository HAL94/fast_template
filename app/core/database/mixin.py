from abc import ABC
from typing import ClassVar, Self, Any
from pydantic import BaseModel
from ._base import Base
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException


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

        obj = self.model(**direct_fields)
        session.add(obj)

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
        if rel_value and isinstance(rel_value, BaseModelDatabaseMixin):
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
            # child_data = await rel_value.create(
            #     session,
            #     rel_value,
            #     commit=commit,
            #     return_as_base=True,
            #     with_relations=True,
            # )
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
            if not item or not isinstance(item, BaseModelDatabaseMixin):
                raise ValueError("data is None or not of type BaseModelDatabaseMixin")
            handler = CreateModelRelations(model=item.model, pydantic=item)
            item_result: Base = await handler.create_with_relations(
                session, item, commit=commit
            )
            sub_data_result.append(item_result)

        setattr(parent_obj, rel_key, sub_data_result)


class BaseModelDatabaseMixin(BaseModel, ABC):
    model: ClassVar[type[Base]]

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        data: BaseModel,
        /,
        *,
        commit: bool = True,
        return_as_base: bool = False,
        exxclude_relations=False,
    ):
        try:
            if exxclude_relations:
                result = await cls.model.create(session, data, commit=commit)
            else:
                handler = CreateModelRelations(model=cls.model, pydantic=data)
                result: Base = await handler.create_with_relations(
                    session, data, commit=False
                )
                if commit:
                    await session.commit()

            if return_as_base:
                return result

            return await cls.get_one(session, result.id)
        except Exception as e:
            raise e

    @classmethod
    async def get_one(
        cls,
        session: AsyncSession,
        val,
        /,
        *,
        field: InstrumentedAttribute | None = None,
        where_clause: list[ColumnElement[bool]] | None = None,
        return_as_base: bool = False,
    ) -> Self:
        result: Base = await cls.model.get_one(
            session, val, field=field, where_clause=where_clause
        )
        if not result:
            raise HTTPException(status_code=404, detail="Not found")

        if return_as_base:
            return result
        return cls.model_validate(result, from_attributes=True)
