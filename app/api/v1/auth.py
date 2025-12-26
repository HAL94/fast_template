from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_async_session
from app.domain.auth import UserWithoutPassword
from app.dto.auth import LoginUserDto, RegisterUserDto, UserSession
from app.services.auth import AuthService

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login")
async def login_user(
    body: Annotated[OAuth2PasswordRequestForm, Depends()], session: AsyncSession = Depends(get_async_session)
) -> UserSession:
    """OAuth2 compatible token login.

    Returns access token and refresh token.
    """
    try:
        auth_service = AuthService(session=session)
        login_body = LoginUserDto(email=body.username, password=body.password)
        return await auth_service.login(login_body)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong") from e


@auth_router.post("/register")
async def register_user(
    body: RegisterUserDto, session: AsyncSession = Depends(get_async_session)
) -> UserWithoutPassword:
    """Register a new user."""
    try:
        auth_service = AuthService(session=session)
        return await auth_service.register(body)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong") from e
