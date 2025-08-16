from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.session import get_async_session
from app.schema import Todo

router = APIRouter(prefix="/todos")


@router.get("/")
async def get_todos(session: AsyncSession = Depends(get_async_session)):
    found_todo = await Todo.get_one(session, 2)
    print(f"found_todo: {found_todo}")
    return found_todo

@router.post("/")
async def create_todo(todo: Todo, session: AsyncSession = Depends(get_async_session)):
    return await Todo.create(session, todo)

