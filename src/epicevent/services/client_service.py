from epicevent.exception import ClientNotFoundError, ClientOwnershipError
from epicevent.infrastructure.unit_of_work import UnitOfWork
from epicevent.models import Client
from epicevent.schemas.client_schema import ClientCreate, ClientUpdate
from epicevent.schemas.types import normalize_email
from epicevent.schemas.user_schema import UserResponse
from epicevent.security.decorators import require_permission
from epicevent.security.permission import Permission


class ClientService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def get_client_by_email(self, client_email: str) -> Client:
        client_email = normalize_email(client_email)
        client = self.uow.clients.find_by_email(client_email)
        if client is None:
            raise ClientNotFoundError()
        return client

    def ensure_client_owner(self, current_user: UserResponse, client: Client):
        if current_user.id != client.sales_representative_id:
            raise ClientOwnershipError()

    @require_permission(Permission.CREATE_CLIENT)
    def create_client(
        self,
        current_user: UserResponse,
        client_dto: ClientCreate,
    ) -> Client:
        with self.uow:
            data = client_dto.model_dump()
            client = Client(**data, sales_representative_id=current_user.id)
            self.uow.clients.save(client)
            return client

    @require_permission(Permission.UPDATE_CLIENT)
    def update_client(
        self,
        current_user: UserResponse,
        client_email: str,
        client_data: ClientUpdate,
    ) -> Client:
        with self.uow:
            client = self.get_client_by_email(client_email)
            self.ensure_client_owner(current_user, client)
            data = client_data.model_dump(exclude_unset=True)
            for field, value in data.items():
                setattr(client, field, value)
            self.uow.clients.save(client)
            return client

    @require_permission(Permission.LIST_CLIENT)
    def list_clients(
        self,
        current_user,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[Client], int]:
        with self.uow:
            clients = self.uow.clients.list(limit=limit, offset=offset)
            total_count = self.uow.clients.count()
            return clients, total_count
