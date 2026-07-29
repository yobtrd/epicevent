from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import epicevent.models  # noqa: F401
from epicevent import bootstrap
from epicevent.cli.console import console
from epicevent.cli.token_storage import get_token_storage
from epicevent.config import TEST_DATABASE_URL
from epicevent.infrastructure.base import Base
from epicevent.infrastructure.repositories.client_repository import ClientRepository
from epicevent.infrastructure.repositories.user_repository import UserRepository
from epicevent.infrastructure.unit_of_work import UnitOfWork
from epicevent.models.client import Client
from epicevent.models.role import Role
from epicevent.models.user import User
from epicevent.schemas.client_schema import ClientCreate
from epicevent.schemas.user_schema import UserCreate
from epicevent.security.roles import UserRole
from epicevent.services.client_service import ClientService
from epicevent.services.password_service import PasswordService
from epicevent.services.token_service import TokenService
from epicevent.services.user_service import UserService


# Database / config
#######################
@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL)

    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)


@pytest.fixture(scope="session")
def create_table_role(engine):
    with Session(engine, expire_on_commit=False) as session:
        management = Role(id=UserRole.MANAGEMENT, name="management")
        sales = Role(id=UserRole.SALES, name="sales")
        support = Role(id=UserRole.SUPPORT, name="support")

        session.add_all([sales, support, management])
        session.commit()


@pytest.fixture
def session(engine, create_table_role):
    connection = engine.connect()

    transaction = connection.begin()

    session = Session(bind=connection, expire_on_commit=False)
    session.close = lambda: None

    try:
        session.begin_nested()
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def uow(session):
    return UnitOfWork(
        session,
        users=UserRepository(session),
        clients=ClientRepository(session),
        use_nested_transaction=True,
    )


@pytest.fixture
def app_factory(session, uow):
    bootstrap.application_factory = bootstrap.ApplicationFactory(
        session_factory=lambda: session,
        use_nested_transaction=True,
    )
    return bootstrap.application_factory


@pytest.fixture
def token_path(monkeypatch, tmp_path):
    path = tmp_path / "token.json"

    monkeypatch.setattr(
        "epicevent.config.TOKEN_PATH",
        path,
    )

    return path


@pytest.fixture
def force_console_width():
    original_width = console.width
    console.width = 1000

    yield

    console.width = original_width


# Services
#######################
@pytest.fixture
def user_service(uow):
    return UserService(
        uow,
        PasswordService(),
    )


@pytest.fixture
def client_service(uow):
    return ClientService(uow)


# Factory - User
#######################
USER_DATA = {
    "employee_number": "002",
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane@test.com",
    "password": "password",
    "role_id": UserRole.MANAGEMENT,
}

USER_MODEL_DATA = {
    "employee_number": "001",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@test.com",
    "password_hash": PasswordService().hash("password"),
    "role_id": 1,
}


def create_user(**kwargs):
    user = {**USER_MODEL_DATA}
    user.update(kwargs)
    user = User(**user)
    return user


def create_persisted_user(session, **kwargs):
    user = {**USER_MODEL_DATA}
    user.update(kwargs)

    persisted_user = User(**user)
    session.add(persisted_user)
    session.flush()
    return persisted_user


def create_user_dto(**kwargs):
    user_dto = {**USER_DATA}
    user_dto.update(kwargs)
    return UserCreate(**user_dto)


@pytest.fixture
def logged_user_factory(session, app_factory, token_path):
    def _create_logged_user(**kwargs):
        defaults = {"employee_number": "000", "email": "logged@test.com"}
        user_params = {**defaults, **kwargs}
        user = create_persisted_user(session, **user_params)

        token_service = TokenService()
        access_token = token_service.create_access_token(user)
        refresh_token = token_service.create_refresh_token(user)

        storage = get_token_storage()
        storage.save(access_token, refresh_token)

        return user

    return _create_logged_user


# Facory - Client
#######################

CLIENT_DATA = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@entreprise.com",
    "phone": "0123456789",
    "business_name": "Doe&Co",
    "first_contact": date(2020, 1, 15),
    "last_contact": date(2023, 11, 20),
}


def create_client(**kwargs):
    client_data = {**CLIENT_DATA}
    client_data.update(kwargs)
    return Client(**client_data)


def create_persisted_client(session, **kwargs):
    client_data = {**CLIENT_DATA}
    client_data.update(kwargs)

    persisted_client = Client(**client_data)
    session.add(persisted_client)
    session.flush()
    return persisted_client


def create_client_dto(**kwargs):
    client_dto = {**CLIENT_DATA}
    client_dto.update(kwargs)
    return ClientCreate(**client_dto)
