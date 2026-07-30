from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from epicevent.schemas.client_schema import ClientResponse
from epicevent.schemas.user_schema import UserResponse


class ContractCreate(BaseModel):
    total_amount: Decimal = Field(max_digits=10, decimal_places=2)
    remaining_amount: Decimal = Field(max_digits=10, decimal_places=2)
    is_signed: bool

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class ContractResponse(BaseModel):
    id: int
    total_amount: Decimal
    remaining_amount: Decimal
    created_at: date
    is_signed: bool
    client: ClientResponse
    sales_representative: UserResponse

    model_config = ConfigDict(
        from_attributes=True,
    )

    @field_validator("created_at", mode="before")
    @classmethod
    def ensure_date_only(cls, value):
        if isinstance(value, datetime):
            return value.date()
        return value


class ContractUpdate(BaseModel):
    total_amount: Decimal | None = Field(default=None)
    remaining_amount: Decimal | None = Field(default=None)
    is_signed: bool | None = Field(default=None)
