from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import VARCHAR, ForeignKey


class Todo(Base):
    __tablename__ = "todos"

    title: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    # Relationships
    subtasks: Mapped[list["Subtask"]] = relationship(back_populates="task", cascade="all, delete")


class Subtask(Base):
    __tablename__ = "subtasks"

    priority: Mapped[int] = mapped_column(nullable=False)
    # Relationships
    todo_id: Mapped[int] = mapped_column(ForeignKey("todos.id"))
    task: Mapped[Todo] = relationship(back_populates="subtasks")
