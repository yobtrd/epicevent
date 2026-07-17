from pydantic import BaseModel

from .user_schema import UserResponse


class TokenPayload(BaseModel):
    sub: int
    type: str
    exp: int
    iat: int


class AuthRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
