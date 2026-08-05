from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from epicevent.schemas.client_schema import ClientResponse
from epicevent.schemas.user_schema import UserResponse

TotalAmount = Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
RemainingAmount = Annotated[Decimal, Field(ge=0, max_digits=10, decimal_places=2)]


class ContractCreate(BaseModel):
    total_amount: TotalAmount
    remaining_amount: RemainingAmount
    is_signed: bool

    model_config = ConfigDict(
        extra="forbid",
    )


class ContractUpdate(BaseModel):
    total_amount: TotalAmount | None = None
    remaining_amount: RemainingAmount | None = None
    is_signed: bool | None = None

    model_config = ConfigDict(
        extra="forbid",
    )


class ContractResponse(BaseModel):
    id: int
    total_amount: Decimal
    remaining_amount: Decimal
    created_at: datetime
    is_signed: bool
    client: ClientResponse
    sales_representative_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class ContractDetailResponse(ContractResponse):
    sales_representative: UserResponse
