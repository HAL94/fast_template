from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import VARCHAR

class Todo(Base):
    __tablename__ = "todos"

    title: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)