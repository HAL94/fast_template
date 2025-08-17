from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload, Load
from sqlalchemy import VARCHAR, ForeignKey

class Todo(Base):
    __tablename__ = "todos"

    @staticmethod
    def get_select_in_load() -> list[Load]:
        return [selectinload(Todo.subtasks)]
    
    title: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    # Relationships
    subtasks: Mapped[list["Subtask"]] = relationship(back_populates="task")

class Subtask(Base):
    __tablename__ = "subtasks"

    priority: Mapped[int] = mapped_column(nullable=False)
    # Relationships
    todo_id: Mapped[int] = mapped_column(ForeignKey("todos.id"))
    task: Mapped[Todo] = relationship(back_populates="subtasks")

