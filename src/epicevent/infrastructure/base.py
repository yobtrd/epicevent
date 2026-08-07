from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from epicevent.config.settings import settings

engine = create_engine(settings.database_url)

SessionFactory = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass
