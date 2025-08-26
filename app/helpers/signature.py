from typing import Any
from itsdangerous import URLSafeTimedSerializer
from app.core.config import settings


class TokenSigner(URLSafeTimedSerializer):
    def __init__(self, max_age: int = 60000, **kwargs):
        secret_key = settings.SESSION_SECRET
        self.max_age = max_age
        super().__init__(secret_key=secret_key, **kwargs)

    def serialize(self, value: Any) -> str:
        return self.dumps(value)

    def deserialize(self, signed_value: str) -> Any | None:
        try:
            return self.loads(signed_value, max_age=self.max_age)
        except Exception:
            return None  # Return None if token is invalid or expired

signer = TokenSigner()