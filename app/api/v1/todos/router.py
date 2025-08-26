from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.session import get_async_session
from app.schema import Todo
from app.core.oauth import get_user_info
import logging

router = APIRouter(prefix="/todos")

logger = logging.getLogger("uvicorn.info")
logger.setLevel(logging.INFO)

@router.get("/{todo_id}")
async def get_todos(
    todo_id: int,    
    user: dict = Depends(get_user_info),
    session: AsyncSession = Depends(get_async_session),
):    
    logger.info(f"User: {user}")
    return await Todo.get_one(session, todo_id)
    

@router.post("/")
async def create_todo(todo: Todo, session: AsyncSession = Depends(get_async_session)):
    return await Todo.create(session, todo)

