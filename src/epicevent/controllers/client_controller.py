from pydantic import ValidationError

from epicevent.exception import InvalidInputError
from epicevent.schemas.client_schema import (
    ClientFullResponse,
    ClientResponse,
    ClientUpdate,
)
from epicevent.schemas.user_schema import UserResponse
from epicevent.services.client_service import ClientCreate, ClientService


class ClientController:
    def __init__(self, client_service: ClientService):
        self.client_service = client_service

    def get_client_by_email(self, client_email: str) -> ClientResponse:
        client = self.client_service.get_client_by_email(client_email)
        return ClientResponse.model_validate(client)

    def verify_client_owner(self, current_user: UserResponse, client: ClientResponse):
        self.client_service.verify_client_owner(current_user, client)

    def create_client(self, current_user: UserResponse, data: dict) -> ClientResponse:
        try:
            request = ClientCreate(**data)
        except ValidationError as e:
            raise InvalidInputError(e.errors()) from e

        client = self.client_service.create_client(current_user, request)
        return ClientResponse.model_validate(client)

    def update_client(
        self, current_user: UserResponse, client_email: str, data: dict
    ) -> ClientResponse:
        try:
            request = ClientUpdate(**data)
        except ValidationError as e:
            raise InvalidInputError(e.errors()) from e
        client = self.client_service.update_client(current_user, client_email, request)
        return ClientResponse.model_validate(client)

    def list_client(
        self, current_user, limit: int = 10, offset: int = 0
    ) -> tuple[list[ClientFullResponse], int]:
        clients_list, total_count = self.client_service.list_client(
            current_user,
            limit=limit,
            offset=offset,
        )
        return (
            [ClientFullResponse.model_validate(client) for client in clients_list],
            total_count,
        )
