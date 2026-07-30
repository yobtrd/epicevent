from epicevent.infrastructure.unit_of_work import UnitOfWork
from epicevent.models.client import Client
from epicevent.models.contract import Contract
from epicevent.schemas.contract_schema import ContractCreate
from epicevent.schemas.user_schema import UserResponse
from epicevent.security.decorators import require_permission
from epicevent.security.permission import Permission


class ContractService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    @require_permission(Permission.CREATE_CONTRACT)
    def create_contract(
        self, current_user: UserResponse, client: Client, contract_dto: ContractCreate
    ):
        with self.uow:
            data = contract_dto.model_dump()
            contract = Contract(
                **data,
                client_id=client.id,
                sales_representative_id=client.sales_representative_id,
            )
            self.uow.contracts.save(contract)
            return contract
