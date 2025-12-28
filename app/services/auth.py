import logging
from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistException, UnauthorizedException
from app.core.security.jwt import JwtManager, hash_password, verify_password
from app.core.security.schema import TokenType
from app.domain.auth import UserBase, UserWithoutPassword
from app.domain.session import SessionBase
from app.dto.auth import LoginUserDto, RegisterUserDto, UserSession
from app.services.base import BaseService

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)


class AuthService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self._user = UserBase
        self._user_without_pw = UserWithoutPassword
        self._session = SessionBase

    def _get_model(self) -> type[UserBase]:
        """Return the model class this service works with."""
        return self._user

    async def register(self, data: RegisterUserDto) -> UserWithoutPassword:
        try:
            # verify if exists, will throw if not by default
            found_user = await self._user.get_one(
                self.session, data.email, field=self._user.model.email, raise_not_found=False
            )

            if found_user:
                raise AlreadyExistException

            hashed_password = hash_password(data.password)
            create_user = UserBase(
                full_name=data.full_name,
                email=data.email,
                hashed_password=hashed_password,
            )

            result = await self._user.create(self.session, create_user)

            return self._user_without_pw.model_validate(result)
        except Exception as e:
            logger.info(f"[AuthService-register]: {e}")
            raise e

    async def login(self, data: LoginUserDto) -> Tuple[UserSession, UserBase]:
        try:
            found_user: UserBase = await self._user.get_one(self.session, data.email, field=self._user.model.email)

            is_match = verify_password(data.password, found_user.hashed_password)

            if not is_match:
                raise UnauthorizedException()

            access_token = JwtManager.create_token(subject=found_user.email, token_type=TokenType.AccessToken)
            refresh_token = JwtManager.create_token(subject=found_user.email, token_type=TokenType.RefreshToken)
            return UserSession(access_token=access_token, refresh_token=refresh_token), found_user
        except Exception as e:
            logger.info(f"[AuthService-login]: {e}")
            raise e
