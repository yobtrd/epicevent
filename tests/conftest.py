import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine

import src.epicevent.models  # noqa: F401
from src.epicevent.database import Base


@pytest.fixture(scope="session")
def engine():
    load_dotenv()
    test_db_url = os.getenv("TEST_DATABASE_URL")
    if test_db_url is None:
        raise RuntimeError("TEST_DATABASE_URL is not definied.")

    engine = create_engine(test_db_url, echo=True)

    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)
