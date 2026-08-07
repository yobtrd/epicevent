from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from epicevent.config.settings import settings

engine = create_engine(settings.database_url)

SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass
