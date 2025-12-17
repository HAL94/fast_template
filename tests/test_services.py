import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.todo import TodoCreate
from app.services.todo import TodoService


class TestTodoService:
    @pytest.fixture
    def todo_service(self, async_session: AsyncSession) -> TodoService:
        """
        Fixture that provides an instance of the TodoService for testing,
        using the transactional AsyncSession.
        """
        return TodoService(session=async_session)

    @pytest.mark.asyncio
    async def test_create_todo(self, todo_service: TodoService):
        """Test the todo creation"""
        todo_item = TodoCreate(title="1st todo")

        added_todo = await todo_service.create_todo(todo_item)

        assert added_todo is not None
        assert added_todo.id is not None
        assert added_todo.title == todo_item.title

    @pytest.mark.asyncio
    async def test_get_todo(self, todo_service: TodoService):
        """Get a todo by id and check it fetches successfully"""
        todo_id = 1
        todo = await todo_service.get_todo(todo_id)

        assert todo is not None
        assert todo.id == todo_id
        assert todo.title is not None

    @pytest.mark.asyncio
    async def test_get_all_todos(self, todo_service: TodoService):
        """Get all todos"""
        todos = await todo_service.get_todos()

        assert todos is not None
        assert len(todos) != 0
