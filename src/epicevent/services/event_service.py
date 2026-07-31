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
