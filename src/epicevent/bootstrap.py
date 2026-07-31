from collections.abc import Callable
from contextlib import contextmanager

from epicevent.controllers.auth_controller import AuthController
from epicevent.controllers.client_controller import ClientController
from epicevent.controllers.contract_controller import ContractController
from epicevent.controllers.event_controller import EventController
from epicevent.controllers.user_controller import UserController
from epicevent.infrastructure.repositories.client_repository import ClientRepository
from epicevent.infrastructure.repositories.contract_repository import ContractRepository
from epicevent.infrastructure.repositories.event_repository import EventRepository
from epicevent.infrastructure.repositories.user_repository import UserRepository
from epicevent.infrastructure.unit_of_work import UnitOfWork
from epicevent.services.auth_service import AuthService
from epicevent.services.client_service import ClientService
from epicevent.services.contract_service import ContractService
from epicevent.services.event_service import EventService
from epicevent.services.password_service import PasswordService
from epicevent.services.user_service import UserService

from .infrastructure.base import SessionLocal


class Application:
    def __init__(
        self,
        auth_controller: AuthController,
        user_controller: UserController,
        client_controller: ClientController,
        contract_controller: ContractController,
        event_controller: EventController,
    ):
        self.auth_controller = auth_controller
        self.user_controller = user_controller
        self.client_controller = client_controller
        self.contract_controller = contract_controller
        self.event_controller = event_controller


class ApplicationFactory:
    def __init__(self, session_factory: Callable, use_nested_transaction: bool = False):
        self.session_factory = session_factory
        self.use_nested_transaction = use_nested_transaction

    @contextmanager
    def create(self):
        session = self.session_factory()

        try:
            user_repo = UserRepository(session)
            client_repo = ClientRepository(session)
            contract_repo = ContractRepository(session)
            event_repo = EventRepository(session)

            uow = UnitOfWork(
                session,
                users=user_repo,
                clients=client_repo,
                contracts=contract_repo,
                events=event_repo,
                use_nested_transaction=self.use_nested_transaction,
            )

            password_service = PasswordService()
            auth_service = AuthService(uow)
            user_service = UserService(uow, password_service)
            client_service = ClientService(uow)
            contract_service = ContractService(uow)
            event_service = EventService(uow)

            app = Application(
                auth_controller=AuthController(auth_service),
                user_controller=UserController(user_service),
                client_controller=ClientController(client_service),
                contract_controller=ContractController(contract_service),
                event_controller=EventController(event_service),
            )

            yield app

        finally:
            session.close()


application_factory = ApplicationFactory(SessionLocal)
