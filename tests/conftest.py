import os

os.environ["ENV_FILE"] = ".env.test"

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import epicevents.models  # noqa: F401
from epicevents import bootstrap
from epicevents.cli.console import console
from epicevents.cli.token_storage import get_token_storage
from epicevents.config.settings import get_settings
from epicevents.infrastructure.base import Base
from epicevents.infrastructure.repositories.client_repository import ClientRepository
from epicevents.infrastructure.repositories.contract_repository import (
    ContractRepository,
)
from epicevents.infrastructure.repositories.event_repository import EventRepository
from epicevents.infrastructure.repositories.user_repository import UserRepository
from epicevents.infrastructure.unit_of_work import UnitOfWork
from epicevents.models.client import Client
from epicevents.models.contract import Contract
from epicevents.models.event import Event
from epicevents.models.role import Role
from epicevents.models.user import User
from epicevents.schemas.client_schema import ClientCreate
from epicevents.schemas.contract_schema import ContractCreate
from epicevents.schemas.event_schema import EventCreate
from epicevents.schemas.user_schema import UserCreate
from epicevents.security.roles import UserRole
from epicevents.services.auth_service import AuthService
from epicevents.services.client_service import ClientService
from epicevents.services.contract_service import ContractService
from epicevents.services.event_service import EventService
from epicevents.services.password_service import PasswordService
from epicevents.services.token_service import TokenService
from epicevents.services.user_service import UserService


# Database / config
#######################
@pytest.fixture(scope="session")
def engine():
    engine = create_engine(get_settings().database_url)

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
        contracts=ContractRepository(session),
        events=EventRepository(session),
        use_nested_transaction=True,
    )


@pytest.fixture
def app_factory(session, monkeypatch):
    factory = bootstrap.ApplicationFactory(
        session_factory=lambda: session,
        use_nested_transaction=True,
    )

    monkeypatch.setattr(
        bootstrap,
        "get_application_factory",
        lambda: factory,
    )

    return factory


@pytest.fixture
def token_path(monkeypatch, tmp_path):
    path = tmp_path / "token.json"
    settings = get_settings()
    settings.token_path = path

    monkeypatch.setattr(
        "epicevents.cli.token_storage.get_settings",
        lambda: settings,
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
def auth_service(uow):
    return AuthService(
        uow,
        TokenService(),
        PasswordService(),
    )


@pytest.fixture
def user_service(uow):
    return UserService(
        uow,
        PasswordService(),
    )


@pytest.fixture
def client_service(uow):
    return ClientService(uow)


@pytest.fixture
def contract_service(uow):
    return ContractService(uow)


@pytest.fixture
def event_service(uow):
    return EventService(uow)


# Factory - User
#######################
USER_DATA = {
    "employee_number": "002",
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane@test.com",
    "password": "Password",
    "role_id": UserRole.MANAGEMENT,
}

USER_MODEL_DATA = {
    "employee_number": "001",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@test.com",
    "password_hash": PasswordService().hash("Password"),
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


# Factory - Client
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


def create_sales_client(
    session,
    email: str = "jon.doe@entreprise.com",
):
    sales_user = create_persisted_user(
        session,
        role_id=UserRole.SALES,
    )

    return create_persisted_client(
        session,
        email=email,
        sales_representative_id=sales_user.id,
    )


# Factory - Contract
#######################
CONTRACT_DATA = {
    "total_amount": Decimal("1000.00"),
    "remaining_amount": Decimal("500.00"),
    "created_at": datetime.now(UTC),
    "is_signed": True,
}


def create_contract(**kwargs):
    contract_data = {**CONTRACT_DATA}
    contract_data.update(kwargs)
    return Contract(**contract_data)


def create_persisted_contract(session, **kwargs):
    contract_data = {**CONTRACT_DATA}
    contract_data.update(kwargs)

    persisted_contract = Contract(**contract_data)
    session.add(persisted_contract)
    session.flush()
    return persisted_contract


def create_contract_dto(**kwargs):
    contract_data = {
        "total_amount": Decimal("1000.00"),
        "remaining_amount": Decimal("1000.00"),
        "is_signed": True,
    }
    contract_data.update(kwargs)
    return ContractCreate(**contract_data)


def create_contract_graph(
    session,
    sales_kwargs=None,
    client_kwargs=None,
    contract_kwargs=None,
):
    sales_kwargs = sales_kwargs or {}
    client_kwargs = client_kwargs or {}
    contract_kwargs = contract_kwargs or {}

    sales = create_persisted_user(
        session,
        role_id=UserRole.SALES,
        **sales_kwargs,
    )

    client = create_persisted_client(
        session,
        sales_representative_id=sales.id,
        **client_kwargs,
    )

    contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales.id,
        **contract_kwargs,
    )

    return contract


# Factory - Event
#######################
EVENT_DATA = {
    "name": "Super évènement",
    "start": datetime(2026, 8, 1, 10, 0),
    "end": datetime(2026, 8, 1, 18, 0),
    "location": "Paris",
    "attendees": 150,
    "notes": "Client VIP",
}


def create_event(**kwargs):
    event_data = {**EVENT_DATA}
    event_data.update(kwargs)
    return Event(**event_data)


def create_persisted_event(session, **kwargs):
    event_data = {**EVENT_DATA}
    event_data.update(kwargs)

    persisted_event = Event(**event_data)
    session.add(persisted_event)
    session.flush()
    return persisted_event


def create_event_dto(**kwargs):
    event_data = {**EVENT_DATA}
    event_data.update(kwargs)
    return EventCreate(**event_data)
