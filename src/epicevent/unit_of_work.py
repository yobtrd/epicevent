from sqlalchemy.orm import Session

from src.epicevent.database import SessionLocal
from src.epicevent.repositories.user_repository import UserRepository


class UnitOfWork:
    def __init__(self):
        self.session: Session | None = None
        self.user: UserRepository | None = None

    def __enter__(self):
        self.session = SessionLocal()

        self.user = UserRepository(self.session)

        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type:
                self.session.rollback()
            else:
                self.session.commit()
        finally:
            self.session.close()
