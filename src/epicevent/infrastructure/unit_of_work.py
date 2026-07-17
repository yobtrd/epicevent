from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from epicevent.infrastructure.repositories.user_repository import UserRepository

from .db_error_translator import translate_database_error


class UnitOfWork:
    """
    Manages database transactions and repository access.

    Acts as a context manager that automatically commits successful operations
    and rolls back failed ones. Integrity errors raised during flush or commit
    are translated into customs exceptions.

    Nested transactions can be enabled for testing purposes to isolate changes
    within an outer transaction.
    """

    def __init__(self, session: Session, use_nested_transaction=False):
        self.session = session
        self.users = UserRepository(session)
        self.use_nested_transaction = use_nested_transaction

    def commit(self):
        if self.use_nested_transaction:
            self.transaction.commit()
        else:
            self.session.commit()

    def rollback(self):
        if self.use_nested_transaction:
            self.transaction.rollback()
        else:
            self.session.rollback()

    def __enter__(self):
        if self.use_nested_transaction:
            self.transaction = self.session.begin_nested()
        return self

    def __exit__(self, exc_type, exc, tb):
        """
        Handles transaction completion.

        Rolls back on exceptions and translates database integrity errors.
        Commits when the context exits successfully and translates commit failures.
        """
        if exc_type:
            self.rollback()
            if isinstance(exc, IntegrityError):
                raise translate_database_error(exc) from exc
            return

        try:
            self.commit()
        except IntegrityError as e:
            self.rollback()
            raise translate_database_error(e) from e
