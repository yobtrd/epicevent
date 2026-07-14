from datetime import UTC, datetime, timedelta

import jwt

from src.epicevent.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
)
from src.epicevent.exception import InvalidTokenTypeError
from src.epicevent.models.user import User
from src.epicevent.schemas.auth import TokenPayload


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
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

        if token_type and payload.get("type") != token_type:
            raise InvalidTokenTypeError()

        return TokenPayload.model_validate(payload)
