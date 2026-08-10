from epicevent.controllers.base_controller import BaseController
from epicevent.schemas.contract_schema import (
    ContractCreate,
    ContractDetailResponse,
    ContractResponse,
    ContractUpdate,
)
from epicevent.schemas.user_schema import UserResponse
from epicevent.services.contract_service import ContractService


class ContractController(BaseController):
    """Coordinate contract operations between CLI and services."""

    def __init__(self, contract_service: ContractService) -> None:
        self.contract_service = contract_service

    def get_contract_by_id(self, contract_id: int) -> ContractResponse:
        contract = self.contract_service.get_contract_by_id(contract_id)
        return ContractResponse.model_validate(contract)

    def ensure_can_update_contract(
        self,
        current_user: UserResponse,
        contract: ContractResponse,
    ) -> None:
        self.contract_service.ensure_can_update_contract(
            current_user,
            contract.client,
        )

    def create_contract(
        self,
        current_user: UserResponse,
        client_email: str,
        data: dict,
    ) -> ContractResponse:
        request = self._validate(ContractCreate, data)
        contract = self.contract_service.create_contract(
            current_user,
            client_email,
            request,
        )
        return ContractResponse.model_validate(contract)

    def update_contract(
        self,
        current_user: UserResponse,
        contract_id: int,
        data: dict,
    ) -> ContractResponse:
        request = self._validate(ContractUpdate, data)
        contract = self.contract_service.update_contract(
            current_user, contract_id, request
        )
        return ContractResponse.model_validate(contract)

    def list_contracts(
        self,
        current_user: UserResponse,
        is_signed: bool | None = None,
        is_paid: bool | None = None,
        sales_assigned: bool = False,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[ContractDetailResponse], int]:
        contracts_list, total_count = self.contract_service.list_contracts(
            current_user,
            is_signed=is_signed,
            is_paid=is_paid,
            sales_assigned=sales_assigned,
            limit=limit,
            offset=offset,
        )
        return (
            [
                ContractDetailResponse.model_validate(contract)
                for contract in contracts_list
            ],
            total_count,
        )

    def show_contract(
        self,
        current_user: UserResponse,
        contract_id: int,
    ) -> ContractDetailResponse:
        contract = self.contract_service.show_contract(current_user, contract_id)
        return ContractDetailResponse.model_validate(contract)
