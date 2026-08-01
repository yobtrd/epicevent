from epicevent.exception import (
    ClientOwnershipError,
    ContractNotFoundError,
    ContractNotSignedError,
)
from epicevent.infrastructure.unit_of_work import UnitOfWork
from epicevent.models.contract import Contract
from epicevent.models.event import Event
from epicevent.schemas.contract_schema import ContractResponse
from epicevent.schemas.event_schema import EventCreate
from epicevent.schemas.user_schema import UserResponse
from epicevent.security.decorators import require_permission
from epicevent.security.permission import Permission


class EventService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def ensure_can_manage_event(
        self,
        current_user: UserResponse,
        contract: Contract | ContractResponse,
    ):
        if current_user.id != contract.client.sales_representative_id:
            raise ClientOwnershipError()
        if not contract.is_signed:
            raise ContractNotSignedError()

    @require_permission(Permission.CREATE_EVENT)
    def create_event(
        self,
        current_user: UserResponse,
        contract_id: int,
        event_dto: EventCreate,
    ):
        with self.uow:
            contract = self.uow.contracts.find_by_id(contract_id)
            if contract is None:
                raise ContractNotFoundError()

            self.ensure_can_manage_event(current_user, contract)

            data = event_dto.model_dump()
            event = Event(**data, contract=contract)
            self.uow.events.save(event)
            return event

    @require_permission(Permission.LIST_EVENT)
    def list_events(
        self,
        current_user: UserResponse,
        is_assigned: bool | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[Event], int]:
        with self.uow:
            events = self.uow.events.list(
                user_id=current_user.id,
                user_role=current_user.role_id,
                is_assigned=is_assigned,
                limit=limit,
                offset=offset,
            )
            total_count = self.uow.events.count(
                user_id=current_user.id,
                user_role=current_user.role_id,
                is_assigned=is_assigned,
            )
            return events, total_count
