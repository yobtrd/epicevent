from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.epicevent.config import DATABASE_URL

engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass
