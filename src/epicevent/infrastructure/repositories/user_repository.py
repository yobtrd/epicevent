from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from epicevent.infrastructure.integrity_error_translator import (
    translate_integrity_error,
)
from epicevent.models.user import User
from epicevent.security.roles import UserRole


class UserRepository:
    """Handle data access operations for users."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, user: User) -> User:
        """
        Persist a user instance in the database.

        Uses flush to catch and translate unique constraint violations
        (email, employee number) into domain exceptions.
        """
        try:
            self.session.add(user)
            self.session.flush()
            return user
        except IntegrityError as exc:
            translate_integrity_error(exc)

    def find_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def find_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.session.scalars(stmt).first()

    def find_by_employee_number(self, employee_number: str) -> User | None:
        stmt = select(User).where(User.employee_number == employee_number)
        return self.session.scalars(stmt).first()

    def _apply_filters(
        self,
        query: Select,
        include_inactive: bool = False,
    ) -> Select:
        """Apply active status filters to the query."""
        if not include_inactive:
            query = query.where(User.is_active.is_(True))

        return query

    def list(
        self,
        include_inactive: bool = False,
        limit: int = 10,
        offset: int = 0,
    ) -> list[User]:
        """Retrieve a paginated list of users matching the active filter."""
        query = select(User)
        query = self._apply_filters(query, include_inactive)
        query = query.offset(offset).limit(limit)

        return self.session.execute(query).scalars().all()

    def count(
        self,
        include_inactive: bool = False,
    ) -> int:
        """Return the total count of users matching the active filter."""
        query = select(User)
        query = self._apply_filters(query, include_inactive)

        count_query = select(func.count()).select_from(query.subquery())
        return self.session.execute(count_query).scalar_one()

    def superuser_exists(self) -> bool:
        """
        Check if at least one active management user exists.

        Return:
            True if one active management user user exists.
        """
        query = select(User.id).where(
            User.role_id == UserRole.MANAGEMENT,
            User.is_active.is_(True),
        )
        return self.session.execute(query).first() is not None
