import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()
db_url = os.getenv("DATABASE_URL")
if db_url is None:
    raise RuntimeError("DATABASE_URL is not definied.")

engine = create_engine(db_url)

Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass
