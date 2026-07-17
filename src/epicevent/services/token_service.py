from datetime import UTC, datetime, timedelta

import jwt
from jwt.exceptions import InvalidTokenError as JWTInvalidTokenError
from pydantic import ValidationError

from epicevent.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
)
from epicevent.exception import InvalidTokenError
from epicevent.models.user import User
from epicevent.schemas.auth_schema import TokenPayload


class TokenService:
    def _now(self):
        return datetime.now(UTC)

    def create_access_token(self, user: User) -> str:
        now = self._now()
        payload = {
            "sub": str(user.id),
            "iat": now,
            "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "type": "access",
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def create_refresh_token(self, user: User) -> str:
        now = self._now()
        payload = {
            "sub": str(user.id),
            "iat": now,
            "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            "type": "refresh",
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def decode_token(self, token: str, token_type: str | None = None) -> TokenPayload:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

            if token_type and payload.get("type") != token_type:
                raise InvalidTokenError()

            return TokenPayload.model_validate(payload)

        except (JWTInvalidTokenError, ValidationError) as exc:
            raise InvalidTokenError() from exc
