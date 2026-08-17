from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from epicevents.schemas.contract_schema import ContractDetailResponse
from epicevents.schemas.user_schema import UserResponse

EventName = Annotated[str, Field(min_length=1, max_length=255)]
Location = Annotated[str, Field(min_length=1, max_length=100)]
Attendees = Annotated[int, Field(ge=1, le=1_000_000)]


class EventCreate(BaseModel):
    name: EventName
    start: datetime
    end: datetime
    location: Location
    attendees: Attendees
    notes: str | None = None

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class EventUpdate(BaseModel):
    name: EventName | None = None
    start: datetime | None = None
    end: datetime | None = None
    location: Location | None = None
    attendees: Attendees | None = None
    notes: str | None = None

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class EventResponse(BaseModel):
    id: int
    name: str
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
