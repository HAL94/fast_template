from uuid import uuid4

from sqlalchemy import UUID, VARCHAR, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    # Relationships
    subtasks: Mapped[list["Subtask"]] = relationship(back_populates="task", cascade="all, delete")


class Subtask(Base):
    __tablename__ = "subtasks"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    priority: Mapped[int] = mapped_column(nullable=True)
    title: Mapped[str] = mapped_column(nullable=True)
    # Relationships
    todo_id: Mapped[UUID] = mapped_column(ForeignKey("todos.id", ondelete="CASCADE"))
    task: Mapped[Todo] = relationship(back_populates="subtasks")
