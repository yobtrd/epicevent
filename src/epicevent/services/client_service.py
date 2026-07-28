from epicevent.infrastructure.unit_of_work import UnitOfWork
from epicevent.models import Client
from epicevent.schemas.client_schema import ClientCreate, ClientResponse
from epicevent.schemas.user_schema import UserResponse
from epicevent.security.decorators import require_permission
from epicevent.security.permission import Permission


class ClientService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

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
