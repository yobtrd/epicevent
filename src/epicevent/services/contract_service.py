from decimal import Decimal

from epicevent.exception import (
    ClientNotFoundError,
    ClientOwnershipError,
    ContractNotFoundError,
    InvalidContractAmountError,
)
from epicevent.infrastructure.unit_of_work import UnitOfWork
from epicevent.models.client import Client
from epicevent.models.contract import Contract
from epicevent.schemas.client_schema import ClientResponse
from epicevent.schemas.contract_schema import ContractCreate, ContractUpdate
from epicevent.schemas.types import normalize_email
from epicevent.schemas.user_schema import UserResponse
from epicevent.security.decorators import require_permission
from epicevent.security.permission import Permission
from epicevent.security.roles import UserRole


class ContractService:
    """Handle contract management operations."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def get_contract_by_id(self, contract_id: int) -> Contract:
        """
        Retrieve a contract by ID.

        Raises:
            ContractNotFoundError: If no contract matches the ID.
        """
        contract = self.uow.contracts.find_by_id(contract_id)
        if contract is None:
            raise ContractNotFoundError()
        return contract

    def ensure_can_update_contract(
        self,
        current_user: UserResponse,
        client: Client | ClientResponse,
    ) -> None:
        """
        Ensure that the user can update a contract.

        Management users bypass ownership checks.
        Sales users must own the associated client.

        Raises:
            ClientOwnershipError: If the user does not own the client.
        """
        if current_user.role_id == UserRole.MANAGEMENT:
            return
        if current_user.id != client.sales_representative_id:
            raise ClientOwnershipError()

    def _validate_contract_amount(
        self,
        total_amount: Decimal,
        remaining_amount: Decimal,
    ) -> None:
        """
        Validate contract amounts.

        The remaining amount cannot exceed the total amount and
        both amounts must be non-negative.

        Raises:
            InvalidContractAmountError: If the amounts are invalid.
        """
        if (
            (total_amount < 0)
            or (remaining_amount < 0)
            or (remaining_amount > total_amount)
        ):
            raise InvalidContractAmountError()

    @require_permission(Permission.CREATE_CONTRACT)
    def create_contract(
        self,
        current_user: UserResponse,
        client_email: str,
        contract_data: ContractCreate,
    ) -> Contract:
        with self.uow:
            client_email = normalize_email(client_email)
            client = self.uow.clients.find_by_email(client_email)
            if client is None:
                raise ClientNotFoundError()

            self._validate_contract_amount(
                contract_data.total_amount,
                contract_data.remaining_amount,
            )

            data = contract_data.model_dump()
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
    ) -> Contract:
        with self.uow:
            contract = self.get_contract_by_id(contract_id)
            self.ensure_can_update_contract(current_user, contract.client)
            data = contract_data.model_dump(exclude_unset=True)

            total_amount = data.get("total_amount", contract.total_amount)
            remaining_amount = data.get("remaining_amount", contract.remaining_amount)
            self._validate_contract_amount(total_amount, remaining_amount)

            for field, value in data.items():
                setattr(contract, field, value)
            return contract

    @require_permission(Permission.LIST_CONTRACT)
    def list_contracts(
        self,
        current_user: UserResponse,
        is_signed: bool | None = None,
        is_paid: bool | None = None,
        sales_assigned: bool = False,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[Contract], int]:
        """
        Retrieve contracts with pagination.

        Returns the paginated contracts and the total matching count.
        """
        with self.uow:
            contracts = self.uow.contracts.list(
                user_id=current_user.id,
                user_role=current_user.role_id,
                is_signed=is_signed,
                is_paid=is_paid,
                sales_assigned=sales_assigned,
                limit=limit,
                offset=offset,
            )
            total_count = self.uow.contracts.count(
                user_id=current_user.id,
                user_role=current_user.role_id,
                is_signed=is_signed,
                is_paid=is_paid,
                sales_assigned=sales_assigned,
            )
            return contracts, total_count
