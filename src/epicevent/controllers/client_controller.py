from pydantic import ValidationError

from epicevent.exception import InvalidInputError
from epicevent.schemas.client_schema import ClientResponse
from epicevent.schemas.user_schema import UserResponse
from epicevent.services.client_service import ClientCreate, ClientService


class ClientController:
    def __init__(self, client_service: ClientService):
        self.client_service = client_service

    def create_client(self, current_user: UserResponse, data: dict) -> ClientResponse:
        try:
            request = ClientCreate(**data)
        except ValidationError as e:
            raise InvalidInputError(e.errors()) from e

        return self.client_service.create_client(current_user, request)
