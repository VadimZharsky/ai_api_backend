from datetime import UTC, datetime

from fastapi import Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User, UserRepository
from app.exceptions import (
    InvalidTokenError,
    InvalidUsernameOrPasswordError,
    TokenNotFoundError,
    UserAlreadyExistsError,
    UserDeactivatedError,
    UserNotFoundError,
)
from app.models import CommonResponse, TokenPayload, UserDataResponse, UserSchema
from app.tools.cookies import CookieHandler
from app.tools.cryptography import Encryptor
from app.tools.jwt import OAuthTool
from app.tools.loggers import ILogger


class AuthService:
    def __init__(self, session: AsyncSession, logger: ILogger) -> None:
        self._session: AsyncSession = session
        self._logger: ILogger = logger

    async def register(self, data: UserSchema) -> CommonResponse:
        is_exist = await UserRepository.assert_user_exists_by_name(
            session=self._session,
            username=data.username,
            logger=self._logger
        )
        if is_exist:
            raise UserAlreadyExistsError("user with username already exists")

        hashed = Encryptor.hash_password(data.password)
        user = User(
            username=data.username,
            password_hash=hashed,
        )
        await UserRepository.create(
            session=self._session,
            entity=user,
            logger=self._logger
        )
        await self._session.commit()
        return CommonResponse(
            message="Registered successfully",
        )

    async def login(self, data: UserSchema, response: Response) -> UserDataResponse:
        user = await UserRepository.get_by_name(
            session=self._session,
            username=data.username,
            logger=self._logger,
        )
        if not user:
            raise InvalidUsernameOrPasswordError("invalid username or password")

        if not Encryptor.verify_password(plain_password=data.password, hashed_password=user.password_hash):
            raise InvalidUsernameOrPasswordError("invalid username or password")

        AuthService._update_tokens(
            user_id=user.id,
            response=response,
        )

        return UserDataResponse(
            id=user.id,
            username=user.username,
            is_active=user.is_active,
            created_at=user.created_at,
        )

    async def refresh(self, request: Request, response: Response) -> CommonResponse:
        refresh_token = CookieHandler.get_refresh_token(request=request)
        if not refresh_token:
            raise TokenNotFoundError("token not found")
        token_payload = OAuthTool.decode_refresh_token(
            token=refresh_token, log=self._logger
        )
        if not token_payload:
            raise InvalidTokenError("invalid token")
        user_id = AuthService._extract_user_id(token=token_payload)
        user = await UserRepository.get(session=self._session, user_id=user_id, logger=self._logger)
        if not user:
            raise UserNotFoundError("user not found")
        if not user.is_active:
            raise UserDeactivatedError("user is deactivated")

        AuthService._update_tokens(
            user_id=user.id,
            response=response,
        )
        return CommonResponse(
            message="Refreshed successfully",
        )
    
    async def get_current_user_id(self, request: Request, response: Response) -> int:
        access_token = CookieHandler.get_access_token(request=request)
        if not access_token:
            raise TokenNotFoundError("token not found")
        token_payload = OAuthTool.decode_access_token(
            token=access_token, log=self._logger
        )
        if not token_payload:
            raise InvalidTokenError("invalid token")
        user_id = AuthService._extract_user_id(token_payload)
        user_exists = await UserRepository.assert_user_exists(
            session=self._session,
            user_id=user_id,
            logger=self._logger
        )
        if not user_exists:
            raise UserNotFoundError("user not found")
        now = datetime.now(tz=UTC)
        CookieHandler.set_access_token(
            response=response,
            token=OAuthTool.create_access_token(user_id=user_id, date=now),
        )
        return user_id

    @staticmethod
    async def logout(response: Response) -> CommonResponse:
        CookieHandler.remove(response=response)
        return CommonResponse(message="Logged out successfully")

    @staticmethod
    def _update_tokens(user_id: int, response: Response) -> None:
        now = datetime.now(tz=UTC)
        CookieHandler.set_access_token(
            response=response,
            token=OAuthTool.create_access_token(user_id=user_id, date=now),
        )
        CookieHandler.set_refresh_token(
            response=response,
            token=OAuthTool.create_refresh_token(user_id=user_id, date=now),
        )

    @staticmethod
    def _extract_user_id(token: TokenPayload) -> int:
        if not token.sub.isdigit():
            raise InvalidTokenError("invalid token")
        return int(token.sub)
