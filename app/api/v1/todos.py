from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.session import get_async_session
from app.dto.todo import TodoCreate
from app.services.todo import TodoService

todos_router = APIRouter(prefix="/todos", tags=["Todos"])


@todos_router.get("/{todo_id}")
async def get_todos(todo_id: int, session: AsyncSession = Depends(get_async_session)):
    return await TodoService.get_todo(session, todo_id)


@todos_router.post("/")
async def create_todo(
    todo: TodoCreate, session: AsyncSession = Depends(get_async_session)
):    
    return await TodoService.create_todo(session, todo)
