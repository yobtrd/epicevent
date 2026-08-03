from datetime import date
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)

from epicevent.schemas.user_schema import UserResponse


def normalize_client_email(value: str) -> str:
    return value.lower().strip()


ClientEmail = Annotated[EmailStr, AfterValidator(normalize_client_email)]


class ClientCreate(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: ClientEmail
    phone: str = Field(min_length=1)
    business_name: str = Field(min_length=1)
    first_contact: date
    last_contact: date

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class ClientUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1)
    last_name: str | None = Field(default=None, min_length=1)
    email: ClientEmail | None = Field(default=None)
    phone: str | None = Field(default=None, min_length=1)
    business_name: str | None = Field(default=None, min_length=1)
    first_contact: date | None = Field(default=None)
    last_contact: date | None = Field(default=None)

    model_config = ConfigDict(
        extra="forbid",
    )


class ClientResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    business_name: str
    first_contact: date
    last_contact: date
    sales_representative_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class ClientDetailResponse(ClientResponse):
    sales_representative: UserResponse | None = None
