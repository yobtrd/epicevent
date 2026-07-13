from sqlalchemy import select
from sqlalchemy.orm import Session

from src.epicevent.models.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()

        return user

    def find_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def find_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)

        return self.session.scalars(stmt).first()
