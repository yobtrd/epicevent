from sqlalchemy.orm import Session

from epicevent.repositories.user_repository import UserRepository


class UnitOfWork:
    def __init__(self, session: Session, use_nested_transaction=False):
        self.session = session
        self.users = UserRepository(session)
        self.use_nested_transaction = use_nested_transaction

    def __enter__(self):
        if self.use_nested_transaction:
            self.transaction = self.session.begin_nested()
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            if self.use_nested_transaction:
                self.transaction.rollback()
            else:
                self.session.rollback()
        else:
            if self.use_nested_transaction:
                self.transaction.commit()
            else:
                self.session.commit()
