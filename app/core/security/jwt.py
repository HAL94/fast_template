import logging
from datetime import UTC, datetime, timedelta
from typing import Union

import jwt
from pwdlib import PasswordHash

from app.core.config import settings
from app.core.security.schema import JwtPayload, TokenType

password_hash = PasswordHash.recommended()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)


class JwtManager:
    @classmethod
    def _get_expiry_by_token_type(cls, token_type: TokenType) -> float:
        if token_type == TokenType.AccessToken:
            return float(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        elif token_type == TokenType.RefreshToken:
            return float(settings.REFRESH_TOKEN_EXPIRE_MINUTES)

        raise ValueError(f"Unknown type of {token_type}")

    @classmethod
    def create_token(cls, *, subject: str, token_type: TokenType, expire_delta: Union[timedelta | None] = None) -> str:
        try:
            logger.info(f"[JwtManager]: creating toke with subject: {subject} and type: {token_type}")
            if subject is None:
                raise ValueError("'subject' cannot be None")
            if token_type is None:
                raise ValueError("'token_type' cannot be None")

            if expire_delta is None:
                exp = datetime.now(tz=UTC) + timedelta(minutes=cls._get_expiry_by_token_type(token_type))
            else:
                exp = datetime.now(tz=UTC) + expire_delta

            payload = JwtPayload(sub=subject, exp=exp, type=token_type)

            return jwt.encode(payload.model_dump(by_alias=False), settings.JWT_SECRET, algorithm=settings.ALGORITHM)
        except Exception as e:
            raise e

    @classmethod
    def verify_token(cls, *, token: str) -> JwtPayload:
        try:
            result = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])

            return JwtPayload.model_validate(result, from_attributes=True)
        except Exception as e:
            raise e
