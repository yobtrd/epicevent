import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import epicevent.models  # noqa: F401
from epicevent import bootstrap
from epicevent.cli.helpers import get_token_storage
from epicevent.config import TEST_DATABASE_URL
from epicevent.infrastructure.base import Base
from epicevent.infrastructure.unit_of_work import UnitOfWork
from epicevent.models.role import Role
from epicevent.models.user import User
from epicevent.schemas.user_schema import UserCreate
from epicevent.security.roles import RoleId
from epicevent.services.authorization_service import AuthorizationService
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
        management = Role(id=RoleId.MANAGEMENT, name="management")
        sales = Role(id=RoleId.SALES, name="sales")
        support = Role(id=RoleId.SUPPORT, name="support")

        session.add_all([sales, support, management])
        session.commit()


@pytest.fixture
def session(engine, create_table_role):
    connection = engine.connect()

    transaction = connection.begin()

    session = Session(bind=connection, expire_on_commit=False)

    try:
        yield session
    finally:
        transaction.rollback()
        connection.close()
        session.close()


@pytest.fixture
def uow(session):
    return UnitOfWork(session, use_nested_transaction=True)


@pytest.fixture
def app_factory(session, uow):
    bootstrap.application_factory = bootstrap.ApplicationFactory(
        lambda: session, lambda _: uow
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


# Logged user
#######################
@pytest.fixture
def logged_management_user(session, app_factory, token_path):
    user = create_persisted_user(
        session,
        email="manager@test.com",
        role_id=RoleId.MANAGEMENT,
    )

    token_service = TokenService()

    access_token = token_service.create_access_token(user)
    refresh_token = token_service.create_refresh_token(user)

    storage = get_token_storage()
    storage.save(
        access_token,
        refresh_token,
    )

    return user


@pytest.fixture
def logged_sales_user(session, app_factory, token_path):
    user = create_persisted_user(
        session,
        email="sales@test.com",
        role_id=RoleId.SALES,
    )

    token_service = TokenService()

    access_token = token_service.create_access_token(user)
    refresh_token = token_service.create_refresh_token(user)

    storage = get_token_storage()
    storage.save(
        access_token,
        refresh_token,
    )

    return user


# Services
#######################
@pytest.fixture
def user_service(uow):
    return UserService(
        uow,
        AuthorizationService(),
    )


# Factory
#######################
USER_DATA = {
    "employee_number": "002",
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane@test.com",
    "password": "password",
    "role_id": RoleId.MANAGEMENT,
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
