from typing import Optional
from pydantic import BaseModel


class TokenExchangeRequest(BaseModel):
    code: str
    code_verifier: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    grant_type: str
    client_id: str
    client_secret: str
    refresh_token: str