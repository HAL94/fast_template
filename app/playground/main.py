import asyncio
from datetime import datetime

from sqlalchemy import and_, or_
from sqlalchemy.orm import selectinload

from app.core.database import session_manager
from app.models import Todo
from app.domain.todo import TodoBase
from app.repositories.todo_repository import TodoRepository


async def run_pg():
    async with session_manager.session() as session:
        repo = TodoRepository(session=session)

        # todo_counts = await repo.count()
        # print(f"Count of todos: {todo_counts}")

        # created_todo = await repo.create({ "title": "New Todo" }, commit=True)
        # print(f"newly created todo: {created_todo}, {type(created_todo)}")

        # todos_paginated_result = await repo.get_many(options=[selectinload(Todo.subtasks)])
        # assert len(todos_paginated_result.result) == 5
        # print(f"[TodoRepo] get_all: {todos_paginated_result}")

        # await repo.create_many(
        #     [
        #         {"title": "First Task in batch"},
        #         {"title": "Second Task in batch"},
        #         {"title": "Third Task in batch"},
        #         {"title": "Fourth Task in batch"},
        #         {"title": "Fifth Task in batch"},
        #     ],
        #     commit=False,
        # )
        # await repo.create_one()
        # exists_ = await repo.exists(
        #     [Todo.created_at.between(datetime(2026, 4, 1), datetime(2026, 4, 30))], as_not_exists=True
        # )
        # print(f"Do we have records with title like 'Task'? {'YES' if exists_ else 'NO'}")
        april_todos = Todo.created_at.between(datetime(2026, 2, 1), datetime(2026, 4, 28))
        # contains_task_keyword = Todo.title.ilike("%item%")

        # paginated_result = await repo.get_many(
        #     where_clause=[or_(april_todos, contains_task_keyword)],
        #     order_clause=[Todo.created_at.desc()],
        #     options=[selectinload(Todo.subtasks)],
        # )

        # updated_todos = await repo.update_many_by_where([april_todos], {"title": "April Task"})
        # print(f"updated_todos: {updated_todos}")

        result = await repo.update_many_by_pk(
            [
                {"title": "April Task 1", "id": 45},
                {"title": "April Task 2", "id": 46},
                {"title": "April Task 3", "id": 47},
            ]
        )
        await session.commit()
        # print(Todo.columns())
        print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(run_pg())
