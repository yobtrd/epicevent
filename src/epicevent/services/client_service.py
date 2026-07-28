from epicevent.exception import ClientNotFoundError, ClientOwnershipError
from epicevent.infrastructure.unit_of_work import UnitOfWork
from epicevent.models import Client
from epicevent.schemas.client_schema import (
    ClientCreate,
    ClientResponse,
    ClientUpdate,
    normalize_client_email,
)
from epicevent.schemas.user_schema import UserResponse
from epicevent.security.decorators import require_permission
from epicevent.security.permission import Permission


class ClientService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def get_client_by_mail(self, client_email: str) -> Client:
        client = self.uow.clients.find_by_email(client_email)
        if client is None:
            raise ClientNotFoundError()
        return client

    @require_permission(Permission.CREATE_CLIENT)
    def create_client(
        self,
        current_user: UserResponse,
        client_dto: ClientCreate,
    ) -> ClientResponse:
        with self.uow:
            data = client_dto.model_dump()
            client = Client(**data, sales_representative_id=current_user.id)
            self.uow.clients.save(client)
            return ClientResponse.model_validate(client)

    @require_permission(Permission.UPDATE_CLIENT)
    def update_client(
        self,
        current_user: UserResponse,
        client_email: str,
        client_data: ClientUpdate,
    ):
        client_email = normalize_client_email(client_email)
        with self.uow:
            client = self.get_client_by_mail(client_email)
            if current_user.id != client.sales_representative_id:
                raise ClientOwnershipError()
            data = client_data.model_dump(exclude_unset=True)
            for field, value in data.items():
                setattr(client, field, value)
            self.uow.clients.save(client)
