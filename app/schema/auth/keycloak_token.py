from typing import Any, Optional
from fastapi import HTTPException, Request
import httpx
from pydantic import BaseModel, Field

from app.helpers import APIClient
from app.schema.auth.request import TokenExchangeRequest, RefreshTokenRequest
from app.schema.auth.code_exchange import TokenExchangeData
from app.core.config import settings


class OAuthTokenBase(BaseModel):
    access_token: str
    expires_in: int
    refresh_expires_in: int
    refresh_token: str
    token_type: str
    id_token: str
    not_before_policy: Optional[int] = Field(alias="not-before-policy", default=None)
    session_state: str
    scope: str


class OAuthToken(OAuthTokenBase):
    @classmethod
    async def exchange(cls, data: TokenExchangeRequest, request: Request):
        async with httpx.AsyncClient() as client:
            code = data.code
            token_exchange_req = {
                "grant_type": "authorization_code",
                "client_id": settings.KEYCLOAK_CLIENT_ID,
                "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.KEYCLOAK_REDIRECT_URI,
                "code_verifier": data.code_verifier,
            }

            api_client = APIClient(client)

            result: OAuthTokenBase = await api_client.post(
                settings.KEYCLOAK_TOKEN_URL,
                data=token_exchange_req,
                request_schema=TokenExchangeData,
                response_schema=OAuthTokenBase,
                headers={"content-type": "application/x-www-form-urlencoded"},
            )

            tokens = result.model_dump()

            # ['access_token',
            # 'expires_in',
            # 'refresh_expires_in',
            # 'refresh_token', 'token_type',
            # 'id_token', 'not_before_policy',
            # 'session_state', 'scope']

            request.session["user_info"] = {
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token"),
            }

            return {"success": True, **tokens}

    @classmethod
    async def refresh(cls, request: Request):
        try:
            async with httpx.AsyncClient() as client:
                user_info: dict[str, Any] = request.session.get("user_info")

                refresh_token = user_info.get("refresh_token")

                api_client = APIClient(client)

                payload = RefreshTokenRequest(
                    grant_type="refresh_token",
                    client_id=settings.KEYCLOAK_CLIENT_ID,
                    client_secret=settings.KEYCLOAK_CLIENT_SECRET,
                    refresh_token=refresh_token,
                )

                result: OAuthToken = await api_client.post(
                    settings.KEYCLOAK_TOKEN_URL,
                    data=payload.model_dump(),
                    response_schema=OAuthToken,
                    headers={"content-type": "application/x-www-form-urlencoded"},
                )

                tokens = result.model_dump()

                request.session["user_info"] = {
                    "access_token": tokens.get("access_token"),
                    "refresh_token": tokens.get("refresh_token"),
                }

                return {"success": True, **tokens}

        except Exception as e:
            raise HTTPException(
                status_code=401, detail="Unauthorized! Try to login again"
            ) from e
