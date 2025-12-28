from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.jwt import JwtManager
from app.core.security.schema import TokenType
from app.dependencies.auth import get_current_active_user
from app.dependencies.db_session import get_async_session
from app.domain.auth import UserWithoutPassword
from app.dto.auth import LoginUserDto, RegisterUserDto, UserSession
from app.dto.session import CreateSessionDto, LogoutDto
from app.services.auth import AuthService
from app.services.session import SessionService

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login", response_model=UserSession)
async def login_user(
    body: Annotated[OAuth2PasswordRequestForm, Depends()], session: AsyncSession = Depends(get_async_session)
) -> UserSession:
    """OAuth2 compatible token login.

    Returns access token and refresh token.
    """
    try:
        auth_service = AuthService(session=session)
        login_body = LoginUserDto(email=body.username, password=body.password)
        tokens, found_user = await auth_service.login(login_body)

        session_service = SessionService(session=session)
        await session_service.create_session(
            CreateSessionDto(
                refresh_token=tokens.refresh_token,
                expires_at=JwtManager.get_expiry(TokenType.RefreshToken),
                user_id=found_user.id,
            )
        )
        return tokens
    except Exception as e:
        print(f"Got an error: {e}")
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


@auth_router.get("/me")
async def get_user(user: UserWithoutPassword = Depends(get_current_active_user)) -> UserWithoutPassword:
    return user


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: LogoutDto, session: AsyncSession = Depends(get_async_session)):
    try:
        session_service = SessionService(session=session)
        await session_service.logout_from_session(body)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong") from e
