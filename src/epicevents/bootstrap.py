from collections.abc import Callable
from contextlib import contextmanager

from sqlalchemy.orm import Session

from epicevents.controllers.auth_controller import AuthController
from epicevents.controllers.client_controller import ClientController
from epicevents.controllers.contract_controller import ContractController
from epicevents.controllers.event_controller import EventController
from epicevents.controllers.user_controller import UserController
from epicevents.infrastructure.base import get_session_factory
from epicevents.infrastructure.repositories.client_repository import ClientRepository
from epicevents.infrastructure.repositories.contract_repository import (
    ContractRepository,
)
from epicevents.infrastructure.repositories.event_repository import EventRepository
from epicevents.infrastructure.repositories.user_repository import UserRepository
from epicevents.infrastructure.unit_of_work import UnitOfWork
from epicevents.services.auth_service import AuthService
from epicevents.services.client_service import ClientService
from epicevents.services.contract_service import ContractService
from epicevents.services.event_service import EventService
from epicevents.services.password_service import PasswordService
from epicevents.services.token_service import TokenService
from epicevents.services.user_service import UserService


class Application:
    """
    Application facade exposing the available controllers.

    Provides a single access point to the application use cases for
    external interfaces such as the CLI.
    """

    def __init__(
        self,
        auth_controller: AuthController,
        user_controller: UserController,
        client_controller: ClientController,
        contract_controller: ContractController,
        event_controller: EventController,
    ) -> None:
        self.auth_controller = auth_controller
        self.user_controller = user_controller
        self.client_controller = client_controller
        self.contract_controller = contract_controller
        self.event_controller = event_controller


class ApplicationFactory:
    """
    Build the application dependency graph.

    Creates database sessions, repositories, services, and controllers
    for each application context.
    """

    def __init__(
        self,
        session_factory: Callable[[], Session],
        use_nested_transaction: bool = False,
    ) -> None:
        self.session_factory = session_factory
        self.use_nested_transaction = use_nested_transaction

    @contextmanager
    def create(self):
        """
        Create an application context with a dedicated database session.

        The session is closed when the context exits.
        """
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

            token_service = TokenService()
            password_service = PasswordService()

            auth_service = AuthService(uow, token_service, password_service)
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


def get_application_factory() -> ApplicationFactory:
    return ApplicationFactory(get_session_factory())
