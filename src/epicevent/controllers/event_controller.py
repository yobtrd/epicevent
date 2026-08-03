from pydantic import ValidationError

from epicevent.exception import InvalidInputError
from epicevent.schemas.contract_schema import ContractResponse
from epicevent.schemas.event_schema import EventDetailResponse, EventResponse
from epicevent.schemas.user_schema import UserResponse
from epicevent.services.event_service import (
    EventCreate,
    EventService,
    EventUpdate,
)


class EventController:
    def __init__(self, event_service: EventService):
        self.event_service = event_service

    def get_event_by_id(self, event_id: int):
        event = self.event_service.get_event_by_id(event_id)
        return EventResponse.model_validate(event)

    def ensure_can_create_event(
        self, current_user: UserResponse, contract: ContractResponse
    ):
        self.event_service.ensure_can_create_event(current_user, contract)

    def ensure_can_update_event(
        self,
        current_user: UserResponse,
        event: EventResponse,
    ):
        self.event_service.ensure_can_update_event(current_user, event)

    def create_event(
        self,
        current_user: UserResponse,
        contract_id: int,
        data: dict,
    ) -> EventResponse:
        try:
            request = EventCreate(**data)
        except ValidationError as e:
            raise InvalidInputError(e.errors()) from e

        event = self.event_service.create_event(current_user, contract_id, request)
        return EventResponse.model_validate(event)

    def update_event(
        self, current_user: UserResponse, event_id: int, data: dict
    ) -> EventResponse:
        try:
            request = EventUpdate(**data)
        except ValidationError as e:
            raise InvalidInputError(e.errors()) from e

        event = self.event_service.update_event(
            current_user,
            event_id,
            request,
        )

        return EventResponse.model_validate(event)

    def list_events(
        self,
        current_user: UserResponse,
        is_assigned: bool | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[EventDetailResponse], int]:
        events_list, total_count = self.event_service.list_events(
            current_user,
            is_assigned=is_assigned,
            limit=limit,
            offset=offset,
        )
        return (
            [EventDetailResponse.model_validate(event) for event in events_list],
            total_count,
        )

    def assign_support(
        self, current_user: UserResponse, event_id: int, employee_number: str
    ) -> tuple[UserResponse, EventResponse]:
        event_support, event_updated = self.event_service.assign_support(
            current_user,
            event_id=event_id,
            employee_number=employee_number,
        )
        return (
            UserResponse.model_validate(event_support),
            EventResponse.model_validate(event_updated),
        )
