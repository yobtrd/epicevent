from epicevent.exception import ClientOwnershipError, ContractNotFoundError
from epicevent.infrastructure.unit_of_work import UnitOfWork
from epicevent.models.client import Client
from epicevent.models.contract import Contract
from epicevent.schemas.contract_schema import ContractCreate, ContractUpdate
from epicevent.schemas.user_schema import UserResponse
from epicevent.security.decorators import require_permission
from epicevent.security.permission import Permission
from epicevent.security.roles import UserRole


class ContractService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def get_contract_by_id(self, contract_id: int) -> Contract:
        contract = self.uow.contracts.find_by_id(contract_id)
        if contract is None:
            raise ContractNotFoundError()
        return contract

    def ensure_can_manage_contract(self, current_user: UserResponse, client: Client):
        if current_user.role_id == UserRole.MANAGEMENT:
            return
        if current_user.id != client.sales_representative_id:
            raise ClientOwnershipError()

    @require_permission(Permission.CREATE_CONTRACT)
    def create_contract(
        self, current_user: UserResponse, client: Client, contract_dto: ContractCreate
    ):
        with self.uow:
            data = contract_dto.model_dump()
            contract = Contract(
                **data,
                client=client,
                sales_representative_id=client.sales_representative_id,
            )
            self.uow.contracts.save(contract)
            return contract

    @require_permission(Permission.UPDATE_CONTRACT)
    def update_contract(
        self,
        current_user: UserResponse,
        contract_id: int,
        contract_data: ContractUpdate,
    ):
        with self.uow:
            contract = self.get_contract_by_id(contract_id)
            self.ensure_can_manage_contract(current_user, contract.client)
            data = contract_data.model_dump(exclude_unset=True)
            for field, value in data.items():
                setattr(contract, field, value)
            self.uow.contracts.save(contract)
            return contract

    @require_permission(Permission.LIST_CONTRACT)
    def list_contracts(
        self,
        current_user: UserResponse,
        is_signed: bool | None = None,
        is_paid: bool | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[Contract], int]:
        with self.uow:
            contracts = self.uow.contracts.list(
                user_id=current_user.id,
                user_role=current_user.role_id,
                is_signed=is_signed,
                is_paid=is_paid,
                limit=limit,
                offset=offset,
            )
            query_count = self.uow.contracts.count(
                user_id=current_user.id,
                user_role=current_user.role_id,
                is_signed=is_signed,
                is_paid=is_paid,
            )
            return contracts, query_count
