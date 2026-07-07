import pytest
from sqlalchemy import create_engine

import src.epicevent.models  # noqa: F401
from src.epicevent.config import TEST_DATABASE_URL
from src.epicevent.database import Base


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL, echo=True)

    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)
