from datetime import UTC, datetime, timedelta

import jwt
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidTokenError as JWTInvalidTokenError,
)
from pydantic import ValidationError

from epicevents.config.settings import get_settings
from epicevents.exception import ExpiredTokenError, InvalidTokenError
from epicevents.models.user import User
from epicevents.schemas.auth_schema import TokenPayload


class TokenService:
    """Handle JWT token creation and validation."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def _now(self) -> datetime:
        return datetime.now(UTC)

    def create_access_token(self, user: User) -> str:
        now = self._now()
        payload = {
            "sub": str(user.id),
            "iat": now,
            "exp": now + timedelta(minutes=self.settings.access_token_expire_minutes),
            "type": "access",
        }
        return jwt.encode(
            payload, self.settings.secret_key, algorithm=self.settings.algorithm
        )

    def create_refresh_token(self, user: User) -> str:
        now = self._now()
        payload = {
            "sub": str(user.id),
            "iat": now,
            "exp": now + timedelta(days=self.settings.refresh_token_expire_days),
            "type": "refresh",
        }
        return jwt.encode(
            payload, self.settings.secret_key, algorithm=self.settings.algorithm
        )

    def decode_token(
        self,
        token: str,
        token_type: str | None = None,
    ) -> TokenPayload:
        """
        Decode a JWT token and validate its payload.

        Raises:
            ExpiredTokenError: If the token has expired.
            InvalidTokenError: If the token cannot be validated.
        """
        try:
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=self.settings.algorithm,
            )
            if token_type and payload.get("type") != token_type:
                raise InvalidTokenError()
            return TokenPayload.model_validate(payload)

        except ExpiredSignatureError as exc:
            raise ExpiredTokenError from exc
        except (JWTInvalidTokenError, ValidationError) as exc:
            raise InvalidTokenError() from exc
