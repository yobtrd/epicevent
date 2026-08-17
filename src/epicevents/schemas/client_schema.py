from datetime import date
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from epicevents.schemas.types import Email, Name
from epicevents.schemas.user_schema import UserResponse

Phone = Annotated[str, Field(min_length=1, max_length=20)]
BusinessName = Annotated[str, Field(min_length=1, max_length=100)]


class ClientCreate(BaseModel):
    first_name: Name
    last_name: Name
    email: Email
    phone: Phone
    business_name: BusinessName
    first_contact: date
    last_contact: date

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class ClientUpdate(BaseModel):
    first_name: Name | None = None
    last_name: Name | None = None
    email: Email | None = None
    phone: Phone | None = None
    business_name: BusinessName | None = None
    first_contact: date | None = None
    last_contact: date | None = None

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class ClientResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    business_name: str
    first_contact: date
    last_contact: date
    sales_representative_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class ClientDetailResponse(ClientResponse):
    sales_representative: UserResponse
