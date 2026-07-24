from collections.abc import Callable
from contextlib import contextmanager

from epicevent.controllers.auth_controller import AuthController
from epicevent.controllers.user_controller import UserController
from epicevent.infrastructure.repositories.user_repository import UserRepository
from epicevent.infrastructure.unit_of_work import UnitOfWork
from epicevent.services.auth_service import AuthService
from epicevent.services.password_service import PasswordService
from epicevent.services.user_service import UserService

from .infrastructure.base import SessionLocal


class Application:
    def __init__(
        self,
        auth_controller: AuthController,
        user_controller: UserController,
    ):
        self.auth_controller = auth_controller
        self.user_controller = user_controller


class ApplicationFactory:
    def __init__(self, session_factory: Callable, use_nested_transaction: bool = False):
        self.session_factory = session_factory
        self.use_nested_transaction = use_nested_transaction

    @contextmanager
    def create(self):
        session = self.session_factory()

        try:
            user_repo = UserRepository(session)

            uow = UnitOfWork(
                session,
                users=user_repo,
                use_nested_transaction=self.use_nested_transaction,
            )

            password_service = PasswordService()
            auth_service = AuthService(uow)
            user_service = UserService(uow, password_service)

            app = Application(
                auth_controller=AuthController(auth_service),
                user_controller=UserController(user_service),
            )

            yield app

        finally:
            session.close()


application_factory = ApplicationFactory(SessionLocal)
