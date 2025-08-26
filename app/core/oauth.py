from typing import Any
from app.core.config import settings
from fastapi_keycloak_middleware import KeycloakConfiguration
from fastapi import Depends, status, HTTPException, Request
from keycloak import KeycloakOpenID
from jwcrypto.jwt import JWTExpired
import logging

logger = logging.getLogger("uvicorn.info")
logger.setLevel(logging.ERROR)

KEYCLOAK_BASE_URL = settings.KEYCLOAK_SERVER_URL
KEYCLOAK_REALM = settings.KEYCLOAK_REALM
KEYCLOAK_CLIENT_ID = settings.KEYCLOAK_CLIENT_ID
KEYCLOAK_CLIENT_SECRET = settings.KEYCLOAK_CLIENT_SECRET
KEYCLOAK_METADATA = settings.KEYCLOAK_METADATA_URI

keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_BASE_URL,  # https://sso.example.com/auth/
    client_id=KEYCLOAK_CLIENT_ID,  # backend-client-id
    realm_name=KEYCLOAK_REALM,  # example-realm
    client_secret_key=KEYCLOAK_CLIENT_SECRET,  # your backend client secret
    verify=True,
)

keycloak_config = KeycloakConfiguration(
    url=KEYCLOAK_BASE_URL,
    realm=KEYCLOAK_REALM,
    client_id=KEYCLOAK_CLIENT_ID,
    client_secret=KEYCLOAK_CLIENT_SECRET,
)


def get_idp_public_key():
    return (
        "-----BEGIN PUBLIC KEY-----\n"
        f"{keycloak_openid.public_key()}"
        "\n-----END PUBLIC KEY-----"
    )


async def get_request_session(request: Request):
    return request.session.get("user_info")

async def get_from_cookie(user_info: dict[str, Any] = Depends(get_request_session)):
    unauth_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
    )

    if not user_info:
        raise unauth_exc
    try:
        return keycloak_openid.decode_token(
            user_info.get("access_token"), validate=True
        )
    except JWTExpired:
        raise unauth_exc


async def get_user_info(payload: dict = Depends(get_from_cookie)) -> dict[str, Any]:
    try:
        return dict(
            id=payload.get("sub"),
            username=payload.get("preferred_username"),
            email=payload.get("email"),
            first_name=payload.get("given_name"),
            last_name=payload.get("family_name"),
            realm_roles=payload.get("realm_access", {}).get("roles", []),
            client_roles=payload.get("realm_access", {}).get("roles", []),
        )
    except Exception as e:
        logger.error(f"Unauthorized: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),  # "Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
