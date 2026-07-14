from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: int
    type: str
    exp: int
    iat: int
