from epicevent.controllers.base_controller import BaseController
from epicevent.schemas.contract_schema import ContractResponse
from epicevent.schemas.event_schema import (
    EventCreate,
    EventDetailResponse,
    EventResponse,
    EventUpdate,
)
from epicevent.schemas.user_schema import UserResponse
from epicevent.services.event_service import EventService


class EventController(BaseController):
    """Coordinate event operations between CLI and services."""

    def __init__(self, event_service: EventService) -> None:
        self.event_service = event_service

    def get_event_by_id(self, event_id: int) -> EventResponse:
        event = self.event_service.get_event_by_id(event_id)
        return EventResponse.model_validate(event)

    def get_detailed_event_by_id(self, event_id: int) -> EventDetailResponse:
        event = self.event_service.get_event_by_id(event_id)
        return EventDetailResponse.model_validate(event)

    def ensure_can_create_event(
        self,
        current_user: UserResponse,
        contract: ContractResponse,
    ) -> None:
        self.event_service.ensure_can_create_event(current_user, contract)

    def ensure_can_update_event(
        self,
        current_user: UserResponse,
        event: EventResponse,
    ) -> None:
        self.event_service.ensure_can_update_event(current_user, event)

    def create_event(
        self,
        current_user: UserResponse,
        contract_id: int,
        data: dict,
    ) -> EventResponse:
        request = self._validate(EventCreate, data)
        event = self.event_service.create_event(current_user, contract_id, request)
        return EventResponse.model_validate(event)

    def update_event(
        self,
        current_user: UserResponse,
        event_id: int,
        data: dict,
    ) -> EventResponse:
        request = self._validate(EventUpdate, data)
        event = self.event_service.update_event(
            current_user,
            event_id,
            request,
        )
        return EventResponse.model_validate(event)

    def list_events(
        self,
        current_user: UserResponse,
        upcoming: bool = False,
        is_assigned: bool | None = None,
        support_assigned: bool = False,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[EventDetailResponse], int]:
        events_list, total_count = self.event_service.list_events(
            current_user,
            upcoming=upcoming,
            is_assigned=is_assigned,
            support_assigned=support_assigned,
            limit=limit,
            offset=offset,
        )
        return (
            [EventDetailResponse.model_validate(event) for event in events_list],
            total_count,
        )

    def show_event(
        self,
        current_user: UserResponse,
        event_id: int,
    ) -> EventDetailResponse:
        event = self.event_service.show_event(current_user, event_id)
        return EventDetailResponse.model_validate(event)

    def assign_support(
        self,
        current_user: UserResponse,
        event_id: int,
        employee_number: str,
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

    def unassign_support(
        self,
        current_user: UserResponse,
        event_id: int,
    ) -> EventResponse:
        event_updated = self.event_service.unassign_support(current_user, event_id)
        return EventResponse.model_validate(event_updated)
