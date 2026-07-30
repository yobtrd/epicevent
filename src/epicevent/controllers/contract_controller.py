from pydantic import ValidationError

from epicevent.exception import InvalidInputError
from epicevent.schemas.contract_schema import ContractCreate, ContractResponse
from epicevent.schemas.user_schema import UserResponse
from epicevent.services.client_service import ClientService
from epicevent.services.contract_service import ContractService


class ContractController:
    def __init__(
        self, contract_service: ContractService, client_service: ClientService
    ):
        self.contract_service = contract_service
        self.client_service = client_service

    def create_contract(
        self, current_user: UserResponse, client_email: str, data: dict
    ) -> ContractResponse:
        client = self.client_service.get_client_by_email(client_email)
        try:
            request = ContractCreate(**data)
        except ValidationError as e:
            raise InvalidInputError(e.errors()) from e

        contract = self.contract_service.create_contract(current_user, client, request)
        return ContractResponse.model_validate(contract)
