from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.pagination import PaginatedResult
from app.core.schema import AppResponse
from app.dependencies.auth import CurrentUser, get_current_active_user
from app.dependencies.db_session import DbSession
from app.domain.todo import TodoBase, TodoWithTasks
from app.dto.todo import TodoCreate
from app.services.todo import TodoService

todos_router = APIRouter(prefix="/todos", tags=["Todos"], dependencies=[Depends(get_current_active_user)])


@todos_router.get("/")
async def get_toods(session: DbSession, user: CurrentUser) -> AppResponse[PaginatedResult[TodoBase]]:
    service = TodoService(session=session)
    result = await service.get_todos(user.id)
    return AppResponse(data=result)


@todos_router.get("/{todo_id}")
async def get_a_todo(todo_id: UUID, session: DbSession, user: CurrentUser) -> AppResponse[TodoWithTasks]:
    service = TodoService(session=session)
    result = await service.get_todo(todo_id, user.id)
    return AppResponse(data=result)


@todos_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate, session: DbSession, user: CurrentUser) -> AppResponse[TodoWithTasks]:
    service = TodoService(session=session)
    result = await service.create_todo(todo, user.id)
    return AppResponse(data=result)


@todos_router.delete("/{todo_id}")
async def delete_todo(todo_id: UUID, session: DbSession, user: CurrentUser) -> AppResponse[Optional[TodoWithTasks]]:
    service = TodoService(session=session)
    result = await service.delete_todo(todo_id, user.id)
    return AppResponse(data=result)
