from datetime import datetime
from enum import StrEnum

from app.core.schema import BaseModel


class TokenType(StrEnum):
    AccessToken = "access"
    RefreshToken = "refresh"


class JwtPayload(BaseModel):
    sub: str
    exp: datetime
    type: TokenType
