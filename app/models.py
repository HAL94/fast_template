from enum import StrEnum

from sqlalchemy import VARCHAR, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(256), nullable=False)
    email: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[str] = mapped_column(String, default=UserRole.USER.value, nullable=False)

    @property
    def user_role(self) -> UserRole:
        """Get role as enum."""
        return UserRole(self.role)


class Todo(Base):
    __tablename__ = "todos"

    title: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    # Relationships
    subtasks: Mapped[list["Subtask"]] = relationship(back_populates="task", cascade="all, delete")


class Subtask(Base):
    __tablename__ = "subtasks"

    priority: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=True)
    # Relationships
    todo_id: Mapped[int] = mapped_column(ForeignKey("todos.id"))
    task: Mapped[Todo] = relationship(back_populates="subtasks")
