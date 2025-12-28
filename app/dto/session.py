from datetime import datetime
from uuid import UUID

from app.core.schema import BaseModel


class CreateSessionDto(BaseModel):
    refresh_token: str
    expires_at: datetime
    user_id: UUID


class LogoutDto(BaseModel):
    refresh_token: str
