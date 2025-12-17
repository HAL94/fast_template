from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient

from app.dto.todo import TodoCreate


class TestTodoRoutes:
    """Test all todo routes"""

    @pytest.mark.asyncio
    async def test_create_todo(self, client: AsyncClient):
        """Run create endpoint for creating todo"""
        todo_sample = TodoCreate(title="some_todo")
        response = await client.post("/todos/", json=todo_sample.model_dump())

        assert response.status_code == status.HTTP_201_CREATED
        payload: dict[str, Any] = response.json()
        assert payload is not None
        assert isinstance(payload, dict)
        assert payload.get("title") == todo_sample.title
        assert payload.get("id") is not None

    @pytest.mark.asyncio
    async def test_get_todo_by_id(self, client: AsyncClient):
        """Run get endpoint for getting a todo by id"""
        todo_id = 1
        response = await client.get(f"/todos/{todo_id}")

        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload is not None
        assert isinstance(payload, dict)
        assert payload.get("id") == todo_id
        assert payload.get("title") is not None

    @pytest.mark.asyncio
    async def test_get_all_todos(self, client: AsyncClient):
        """Run endpoint to get all todos with a limit of 20 records"""
        response = await client.get("/todos/")
        default_size = 1

        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload is not None
        assert isinstance(payload, list)
        assert len(payload) == default_size
