import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import src.epicevent.models  # noqa: F401
from src.epicevent.config import TEST_DATABASE_URL
from src.epicevent.constants.roles import RoleId
from src.epicevent.database import Base
from src.epicevent.models.user import Role, User
from src.epicevent.schemas.user import UserCreate
from src.epicevent.unit_of_work import UnitOfWork


# Database
###############
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
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def uow(session):
    return UnitOfWork(session, use_nested_transaction=True)


# Factory
###############
USER_DATA = {
    "employee_number": "001",
    "first_name": "Jon",
    "last_name": "Doe",
    "email": "jon@test.com",
    "password": "password",
    "role_id": RoleId.MANAGEMENT,
}

USER_MODEL_DATA = {
    "employee_number": "001",
    "first_name": "Jon",
    "last_name": "Doe",
    "email": "jon@test.com",
    "password_hash": "password",
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
