from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from epicevent.config.settings import get_settings


def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(settings.database_url)


def get_session_factory() -> sessionmaker[Session]:
    """Create a session factory with instances remaining usable after commit."""
    return sessionmaker(
        bind=get_engine(),
        expire_on_commit=False,
    )


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass
