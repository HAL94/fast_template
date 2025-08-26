from typing import Any
from fastapi import APIRouter, Depends, Request
from app.core.oauth import get_user_info
from app.schema import (
    TokenExchangeRequest
)
from app.schema.auth.keycloak_token import OAuthToken

router: APIRouter = APIRouter(prefix="/auth")


@router.post("/token-exchange")
async def exchange_token(data: TokenExchangeRequest, request: Request):
    return await OAuthToken.exchange(data, request)


@router.post("/refresh")
async def refresh_session(request: Request):
    return await OAuthToken.refresh(request)


@router.post("/logout")
async def logout(request: Request):
    del request.session["user_info"]
    return {"success": True}


@router.get("/me")
async def verify(user_data: Any = Depends(get_user_info)):
    return user_data
