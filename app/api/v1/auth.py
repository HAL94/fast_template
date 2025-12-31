from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.jwt import JwtManager
from app.dependencies.auth import RtCookie, get_current_active_user
from app.dependencies.db_session import get_async_session
from app.domain.auth import UserWithoutPassword
from app.dto.auth import LoginUserDto, RegisterUserDto, UserSession
from app.services.auth import AuthService
from app.services.session import SessionService

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login", response_model=UserSession)
async def login_user(
    response: Response,
    body: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_async_session),
) -> UserSession:
    """OAuth2 compatible token login.

    Returns access token and refresh token.
    """
    try:
        auth_service = AuthService(session=session)
        login_body = LoginUserDto(email=body.username, password=body.password)
        tokens = await auth_service.login(login_body)

        response.set_cookie(**JwtManager.rt_cookie_options(tokens.refresh_token))

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
async def logout(rt_encoding: RtCookie, session: AsyncSession = Depends(get_async_session)):
    try:
        session_service = SessionService(session=session)
        await session_service.logout_from_session(JwtManager.validate_rt_cookie(rt_encoding))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong") from e


@auth_router.post("/refresh")
async def refresh_token(rt_encoding: RtCookie, response: Response, session: AsyncSession = Depends(get_async_session)):
    try:
        if not rt_encoding:
            raise HTTPException(status_code=401, detail="Not authorized for refresh")
        auth_service = AuthService(session=session)
        tokens = await auth_service.refresh_session(rt_encoding=rt_encoding)
        response.set_cookie(**JwtManager.rt_cookie_options(tokens.refresh_token))
        return tokens
    except Exception as e:
        raise e
