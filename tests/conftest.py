import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import src.epicevent.models  # noqa: F401
from src.epicevent.config import TEST_DATABASE_URL
from src.epicevent.constants.roles import RoleName
from src.epicevent.database import Base
from src.epicevent.models.user import Role, User


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL, echo=True)

    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)


@pytest.fixture(scope="session")
def roles(engine):
    with Session(engine, expire_on_commit=False) as session:
        sales = Role(name=RoleName.SALES)
        support = Role(name=RoleName.SUPPORT)
        management = Role(name=RoleName.MANAGEMENT)

        session.add_all([sales, support, management])
        session.commit()

        return {
            RoleName.SALES: sales.id,
            RoleName.SUPPORT: support.id,
            RoleName.MANAGEMENT: management.id,
        }


@pytest.fixture
def session(engine, roles):
    connection = engine.connect()
    transaction = connection.begin()

    with Session(bind=connection) as session:
        yield session

    transaction.rollback()
    connection.close()


@pytest.fixture
def user(roles):
    return User(
        employee_number="001",
        first_name="Jon",
        last_name="Doe",
        email="jon@test.com",
        password_hash="password",
        role_id=roles[RoleName.SALES],
    )


@pytest.fixture
def persisted_user(session, user):
    session.add(user)
    session.flush()

    return user
