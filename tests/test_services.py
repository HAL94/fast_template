from typing import AsyncGenerator
from unittest.mock import patch

import pytest
import pytest_asyncio

from app.dto.todo import TodoCreate
from app.services.todo import TodoService


class TestTodoCruds:
    @pytest.fixture
    def mock_todo_service(self, mocker):
        with patch("api.v1.todos.TodoService") as mock_todo_service_class:
            mock_todo_service = mocker.MagicMock(spec=TodoService)
            mock_todo_service_class.return_value = mock_todo_service
            yield mock_todo_service

    @pytest_asyncio.fixture
    async def todo_service(self, test_session) -> AsyncGenerator[TodoService, None]:
        """
        Fixture that provides an instance of the TodoService for testing,
        using the transactional AsyncSession.
        """
        async with test_session() as session:
            service = TodoService(session=session)
            yield service

    @pytest.mark.asyncio
    async def test_create_todo(self, todo_service: TodoService):
        todo_item = TodoCreate(title="1st todo")

        added_todo = await todo_service.create_todo(todo_item)

        assert added_todo is not None
        assert added_todo.id is not None
        assert added_todo.title == todo_item.title
