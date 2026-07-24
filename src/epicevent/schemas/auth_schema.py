from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .user_schema import UserResponse


class TokenPayload(BaseModel):
    sub: int
    type: str
    exp: int
    iat: int

    model_config = ConfigDict(extra="forbid")


class AuthRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str

    model_config = ConfigDict(extra="forbid")


class TokenPairs(BaseModel):
    access_token: str
    refresh_token: str

    model_config = ConfigDict(extra="forbid")


class SessionResult(BaseModel):
    user: UserResponse
    new_tokens: TokenPairs | None = None

    model_config = ConfigDict(extra="forbid")
