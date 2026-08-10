from epicevent.controllers.base_controller import BaseController
from epicevent.schemas.client_schema import (
    ClientCreate,
    ClientDetailResponse,
    ClientResponse,
    ClientUpdate,
)
from epicevent.schemas.user_schema import UserResponse
from epicevent.services.client_service import ClientService


class ClientController(BaseController):
    """Coordinate client operations between CLI and services."""

    def __init__(self, client_service: ClientService) -> None:
        self.client_service = client_service

    def get_client_by_email(self, client_email: str) -> ClientResponse:
        client = self.client_service.get_client_by_email(client_email)
        return ClientResponse.model_validate(client)

    def ensure_client_owner(
        self,
        current_user: UserResponse,
        client: ClientResponse,
    ) -> None:
        self.client_service.ensure_client_owner(current_user, client)

    def create_client(self, current_user: UserResponse, data: dict) -> ClientResponse:
        request = self._validate(ClientCreate, data)
        client = self.client_service.create_client(current_user, request)
        return ClientResponse.model_validate(client)

    def update_client(
        self,
        current_user: UserResponse,
        client_email: str,
        data: dict,
    ) -> ClientResponse:
        request = self._validate(ClientUpdate, data)
        client = self.client_service.update_client(current_user, client_email, request)
        return ClientResponse.model_validate(client)

    def list_clients(
        self,
        current_user: UserResponse,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[ClientDetailResponse], int]:
        clients_list, total_count = self.client_service.list_clients(
            current_user,
            limit=limit,
            offset=offset,
        )
        return (
            [ClientDetailResponse.model_validate(client) for client in clients_list],
            total_count,
        )

    def show_client(
        self,
        current_user: UserResponse,
        client_email: str,
    ) -> ClientDetailResponse:
        client = self.client_service.show_client(current_user, client_email)
        return ClientDetailResponse.model_validate(client)
