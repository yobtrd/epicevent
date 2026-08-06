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
    """Handle event management operations."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def get_event_by_id(self, event_id: int) -> Event:
        """
        Retrieve an event by ID.

        Raises:
            EventNotFoundError: If no event matches the ID.
        """
        event = self.uow.events.find_by_id(event_id)
        if event is None:
            raise EventNotFoundError()
        return event

    def ensure_can_create_event(
        self,
        current_user: UserResponse,
        contract: Contract | ContractResponse,
    ) -> None:
        """
        Ensure that a user can create an event for a contract.

        The sales user must own the associated client and the contract
        must be signed.

        Raises:
            ClientOwnershipError: If the user does not own the client.
            ContractNotSignedError: If the contract is not signed.
        """
        if current_user.id != contract.client.sales_representative_id:
            raise ClientOwnershipError()
        if not contract.is_signed:
            raise ContractNotSignedError()

    def ensure_can_update_event(
        self,
        current_user: UserResponse,
        event: Event | EventResponse,
    ) -> None:
        """
        Ensure that a user can update an event.

        Management users bypass ownership checks.
        Support users must be assigned to the event.

        Raises:
            EventOwnershipError: If the user is not assigned to the event.
        """
        if current_user.role_id == UserRole.MANAGEMENT:
            return

        if current_user.id != event.support_representative_id:
            raise EventOwnershipError()

    def _validate_event_dates(self, start: date, end: date) -> None:
        """Validate that the event end date is not before the start date."""
        if end < start:
            raise InvalidEventDatesError()

    @require_permission(Permission.CREATE_EVENT)
    def create_event(
        self,
        current_user: UserResponse,
        contract_id: int,
        event_data: EventCreate,
    ) -> Event:
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
    ) -> Event:
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
        """
        Retrieve events with pagination.

        Returns the paginated events and the total matching count.
        """
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
        """
        Assign a support representative to an event.

        The assigned user must have the support role.

        Raises:
            EventNotFoundError: If the event does not exist.
            UserNotFoundError: If the support user does not exist.
            SupportAssignmentError: If the user is not support.
        """
        with self.uow:
            event = self.get_event_by_id(event_id)
            support = self.uow.users.find_by_employee_number(employee_number)

            if support is None:
                raise UserNotFoundError()
            if support.role_id != UserRole.SUPPORT:
                raise SupportAssignmentError()

            event.support_representative = support
            self.uow.events.save(event)
            return support, event

    @require_permission(Permission.ASSIGN_SUPPORT)
    def unassign_support(
        self,
        current_user: UserResponse,
        event_id: int,
    ) -> Event:
        """
        Remove the support representative assigned to an event.

        Raises:
            EventNotFoundError: If the event does not exist.
        """
        with self.uow:
            event = self.get_event_by_id(event_id)
            event.support_representative = None
            self.uow.events.save(event)
            return event
