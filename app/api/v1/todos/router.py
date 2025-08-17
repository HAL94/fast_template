from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.session import get_async_session
from app.schema import Todo

router = APIRouter(prefix="/todos")


@router.get("/{todo_id}")
async def get_todos(todo_id: int, session: AsyncSession = Depends(get_async_session)):
    return await Todo.get_one(session, todo_id)
    

@router.post("/")
async def create_todo(todo: Todo, session: AsyncSession = Depends(get_async_session)):
    return await Todo.create(session, todo)
    
    

