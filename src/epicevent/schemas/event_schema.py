from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from epicevent.schemas.contract_schema import ContractDetailResponse
from epicevent.schemas.user_schema import UserResponse


class EventCreate(BaseModel):
    start: datetime
    end: datetime
    location: str = Field(min_length=1)
    attendees: int = Field(ge=1, le=1_000_000)
    notes: str | None = None


class EventResponse(BaseModel):
    id: int
    start: datetime
    end: datetime
    location: str
    attendees: int
    notes: str | None
    contract_id: int
    support_representative_id: int | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class EventDetailResponse(EventResponse):
    contract: ContractDetailResponse
    support_representative: UserResponse | None

    model_config = ConfigDict(
        from_attributes=True,
    )
