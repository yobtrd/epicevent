from pydantic import ValidationError

from epicevent.exception import InvalidInputError
from epicevent.schemas.contract_schema import ContractResponse
from epicevent.schemas.event_schema import EventDetailResponse, EventResponse
from epicevent.schemas.user_schema import UserResponse
from epicevent.services.event_service import EventCreate, EventService


class EventController:
    def __init__(self, event_service: EventService):
        self.event_service = event_service

    def ensure_can_manage_event(
        self, current_user: UserResponse, contract: ContractResponse
    ):
        self.event_service.ensure_can_manage_event(current_user, contract)

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
