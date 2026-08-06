from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from epicevent.config import DATABASE_URL

engine = create_engine(DATABASE_URL)

SessionFactory = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass
