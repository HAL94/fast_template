from typing import Optional
from pydantic import BaseModel, Field


class TokenExchangeResult(BaseModel):
    access_token: str
    expires_in: int
    refresh_expires_in: int
    refresh_token: str
    token_type: str
    id_token: str
    not_before_policy: Optional[int] = Field(alias="not-before-policy", default=None)
    session_state: str
    scope: str