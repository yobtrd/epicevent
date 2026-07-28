from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClientCreate(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: EmailStr
    phone: str = Field(min_length=1)
    business_name: str = Field(min_length=1)
    first_contact: date
    last_contact: date

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
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
        extra="forbid",
        from_attributes=True,
    )
