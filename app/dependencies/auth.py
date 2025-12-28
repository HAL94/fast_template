import logging
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundException
from app.core.security.schema import JwtPayload, TokenType
from app.dependencies.db_session import get_async_session
from app.domain.auth import UserBase, UserWithoutPassword

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: AsyncSession = Depends(get_async_session)
) -> UserWithoutPassword:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        validated_payload = JwtPayload.model_validate(payload)

        if not validated_payload:
            raise credentials_exception
        if validated_payload.type != TokenType.AccessToken:
            raise credentials_exception

        email = validated_payload.sub
        if not email:
            raise credentials_exception

        user_data = await UserBase.get_one(session, email, field=UserBase.model.email)
        if not user_data.is_active:
            raise credentials_exception

        return UserWithoutPassword.model_validate(user_data)
    except jwt.InvalidTokenError:
        raise credentials_exception
    except NotFoundException:
        raise credentials_exception


async def get_current_active_user(
    current_user: Annotated[UserBase, Depends(get_current_user)],
) -> UserWithoutPassword:
    return current_user
