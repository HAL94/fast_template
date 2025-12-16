from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_async_session
from app.domain.todo import TodoWithTasks
from app.dto.todo import TodoCreate
from app.services.todo import TodoService

todos_router = APIRouter(prefix="/todos", tags=["Todos"])


@todos_router.get("/{todo_id}")
async def get_todos(todo_id: int, session: AsyncSession = Depends(get_async_session)) -> TodoWithTasks:
    service = TodoService(session=session)
    return await service.get_todo(todo_id)


@todos_router.post("/")
async def create_todo(todo: TodoCreate, session: AsyncSession = Depends(get_async_session)) -> TodoWithTasks:
    service = TodoService(session=session)
    return await service.create_todo(todo)
