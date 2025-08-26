from pydantic import BaseModel


class TokenExchangeData(BaseModel):
    grant_type: str
    client_id: str
    client_secret: str
    code: str
    redirect_uri: str
    code_verifier: str