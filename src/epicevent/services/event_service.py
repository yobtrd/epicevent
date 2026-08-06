from datetime import date

from epicevent.exception import (
    ClientOwnershipError,
    ContractNotFoundError,
    ContractNotSignedError,
    EventNotFoundError,
    EventOwnershipError,
    InvalidEventDatesError,
    SupportAssignmentError,
    UserNotFoundError,
)
from epicevent.infrastructure.unit_of_work import UnitOfWork
from epicevent.models.contract import Contract
from epicevent.models.event import Event
from epicevent.models.user import User
from epicevent.schemas.contract_schema import ContractResponse
from epicevent.schemas.event_schema import (
    EventCreate,
    EventResponse,
    EventUpdate,
)
from epicevent.schemas.user_schema import UserResponse
from epicevent.security.decorators import require_permission
from epicevent.security.permission import Permission
from epicevent.security.roles import UserRole


class EventService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def get_event_by_id(self, event_id: int) -> Event:
        event = self.uow.events.find_by_id(event_id)
        if event is None:
            raise EventNotFoundError()
        return event

    def ensure_can_create_event(
        self,
        current_user: UserResponse,
        contract: Contract | ContractResponse,
    ):
        if current_user.id != contract.client.sales_representative_id:
            raise ClientOwnershipError()
        if not contract.is_signed:
            raise ContractNotSignedError()

    def ensure_can_update_event(
        self,
        current_user: UserResponse,
        event: Event | EventResponse,
    ):
        if current_user.role_id == UserRole.MANAGEMENT:
            return

        if current_user.id != event.support_representative_id:
            raise EventOwnershipError()

    def _validate_event_dates(self, start: date, end: date) -> None:
        if end < start:
            raise InvalidEventDatesError()

    @require_permission(Permission.CREATE_EVENT)
    def create_event(
        self,
        current_user: UserResponse,
        contract_id: int,
        event_data: EventCreate,
    ):
        with self.uow:
            contract = self.uow.contracts.find_by_id(contract_id)
            if contract is None:
                raise ContractNotFoundError()

            self.ensure_can_create_event(current_user, contract)
            self._validate_event_dates(event_data.start, event_data.end)

            data = event_data.model_dump()
            event = Event(**data, contract=contract)
            self.uow.events.save(event)
            return event

    @require_permission(Permission.UPDATE_EVENT)
    def update_event(
        self,
        current_user: UserResponse,
        event_id: int,
        event_data: EventUpdate,
    ):
        with self.uow:
            event = self.get_event_by_id(event_id)
            self.ensure_can_update_event(current_user, event)

            data = event_data.model_dump(exclude_unset=True)
            start = data.get("start", event.start)
            end = data.get("end", event.end)
            self._validate_event_dates(start, end)

            for field, value in data.items():
                setattr(event, field, value)
            self.uow.events.save(event)
            return event

    @require_permission(Permission.LIST_EVENT)
    def list_events(
        self,
        current_user: UserResponse,
        upcoming: bool = False,
        is_assigned: bool | None = None,
        support_assigned: bool = False,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[Event], int]:
        with self.uow:
            events = self.uow.events.list(
                user_id=current_user.id,
                user_role=current_user.role_id,
                upcoming=upcoming,
                is_assigned=is_assigned,
                support_assigned=support_assigned,
                limit=limit,
                offset=offset,
            )
            total_count = self.uow.events.count(
                user_id=current_user.id,
                user_role=current_user.role_id,
                upcoming=upcoming,
                is_assigned=is_assigned,
                support_assigned=support_assigned,
            )
            return events, total_count

    @require_permission(Permission.ASSIGN_SUPPORT)
    def assign_support(
        self,
        current_user: UserResponse,
        event_id: int,
        employee_number: str,
    ) -> tuple[User, Event]:
        with self.uow:
            event = self.get_event_by_id(event_id)
            support = self.uow.users.find_by_employee_number(employee_number)

            if support is None:
                raise UserNotFoundError()
            if support.role_id != UserRole.SUPPORT:
                raise SupportAssignmentError()

            event.support_representative = support
            return support, event

    @require_permission(Permission.ASSIGN_SUPPORT)
    def unassign_support(self, current_user: UserResponse, event_id: int) -> Event:
        with self.uow:
            event = self.get_event_by_id(event_id)
            event.support_representative = None
            return event
