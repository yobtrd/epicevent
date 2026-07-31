from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from epicevent.exception import (
    EmailAlreadyExistsError,
    EmployeeNumberAlreadyExistsError,
)
from epicevent.models.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def _translate_integrity_error(self, exc):
        constraint = exc.orig.diag.constraint_name

        match constraint:
            case "user_email_key":
                raise EmailAlreadyExistsError() from exc

            case "user_employee_number_key":
                raise EmployeeNumberAlreadyExistsError() from exc

    def save(self, user: User) -> User:
        try:
            self.session.add(user)
            self.session.flush()
            return user
        except IntegrityError as exc:
            self._translate_integrity_error(exc)

    def find_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def find_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.session.scalars(stmt).first()

    def find_by_employee_number(self, employee_number: str) -> User | None:
        stmt = select(User).where(User.employee_number == employee_number)
        return self.session.scalars(stmt).first()
