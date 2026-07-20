from datetime import datetime, timedelta

from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import ValidationError

from app.exceptions import TokenExpiredError, TokenNotFoundError
from app.models import TokenPayload
from app.tools.loggers import ILogger
from app_config import app_settings


class OAuthTool:
    @staticmethod
    def create_access_token(user_id: int, date: datetime) -> str:
        return OAuthTool._create(
            user_id=user_id,
            secret=app_settings.AUTH.jwt_secret,
            expires=app_settings.AUTH.jwt_expires_min,
            date=date,
        )

    @staticmethod
    def create_refresh_token(user_id: int, date: datetime) -> str:
        return OAuthTool._create(
            user_id=user_id,
            secret=app_settings.AUTH.jwt_refresh_secret,
            expires=app_settings.AUTH.jwt_refresh_expires_min,
            date=date,
        )

    @staticmethod
    def decode_access_token(token: str | None, log: ILogger) -> TokenPayload | None:
        return OAuthTool._decode(token=token, secret=app_settings.AUTH.jwt_secret, log=log)

    @staticmethod
    def decode_refresh_token(token: str | None, log: ILogger) -> TokenPayload | None:
        return OAuthTool._decode(token=token, secret=app_settings.AUTH.jwt_refresh_secret, log=log)

    @staticmethod
    def _decode(token: str | None, secret: str, log: ILogger) -> TokenPayload | None:
        if token is None:
            raise TokenNotFoundError("token not found")
        try:
            payload = jwt.decode(token, secret, algorithms=app_settings.AUTH.jwt_algorithm)
            return TokenPayload.model_validate(payload)

        except ExpiredSignatureError as exc:
            log.error(f"OAUTH >> JWT expired: {exc!s}")
            raise TokenExpiredError("token expired") from exc
        except JWTError as exc:
            log.error(f"OAUTH >> JWT Error: {exc!s}")
        except ValidationError as exc:
            log.error(f"OAUTH >> pydantic Error: {exc!s}")
        except Exception as exc:
            log.error(f"OAUTH >> exception: {exc!s}")

    @staticmethod
    def _create(user_id: int, expires: int, secret: str, date: datetime) -> str:
        payload = TokenPayload(
            iat=date,
            nbf=date,
            exp=date + timedelta(minutes=expires),
            sub=str(user_id),
        )
        return jwt.encode(payload.model_dump(), secret, algorithm=app_settings.AUTH.jwt_algorithm)