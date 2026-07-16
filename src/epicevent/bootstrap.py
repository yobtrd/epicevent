from collections.abc import Callable
from contextlib import contextmanager

from epicevent.controllers.auth_controller import AuthController
from epicevent.services.auth_service import AuthService
from epicevent.unit_of_work import UnitOfWork

from .database import SessionLocal


class Application:
    def __init__(self, uow: UnitOfWork):
        self.auth = AuthController(AuthService(uow))


class ApplicationFactory:
    def __init__(self, session_factory: Callable, uow_factory: Callable = UnitOfWork):
        self.session_factory = session_factory
        self.uow_factory = uow_factory

    @contextmanager
    def create(self):
        session = self.session_factory()

        try:
            uow = self.uow_factory(session)
            yield Application(uow)

        finally:
            session.close()


application_factory = ApplicationFactory(SessionLocal)
