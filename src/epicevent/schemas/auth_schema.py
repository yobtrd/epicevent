from pydantic import BaseModel, ConfigDict

from epicevent.schemas.types import Email
from epicevent.schemas.user_schema import UserResponse


class TokenPayload(BaseModel):
    sub: int
    type: str
    exp: int
    iat: int


class AuthRequest(BaseModel):
    email: Email
    password: str

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str


class TokenPairs(BaseModel):
    access_token: str
    refresh_token: str


class SessionResult(BaseModel):
    user: UserResponse
    new_tokens: TokenPairs | None = None
