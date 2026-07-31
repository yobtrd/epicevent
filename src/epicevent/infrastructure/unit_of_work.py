from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from epicevent.exception import DatabaseError
from epicevent.infrastructure.repositories.client_repository import ClientRepository
from epicevent.infrastructure.repositories.contract_repository import ContractRepository
from epicevent.infrastructure.repositories.event_repository import EventRepository
from epicevent.infrastructure.repositories.user_repository import UserRepository


class UnitOfWork:
    """
    Manages database transactions and repository access.

    Acts as a context manager that automatically commits successful operations
    and rolls back failed ones. Unknown integrity errors raised during commit are
    translated into generic application exceptions..

    Nested transactions can be enabled for testing purposes to isolate changes
    within an outer transaction.
    """

    def __init__(
        self,
        session: Session,
        users: UserRepository,
        clients: ClientRepository,
        contracts: ContractRepository,
        events: EventRepository,
        use_nested_transaction=False,
    ):
        self.session = session
        self.users = users
        self.clients = clients
        self.contracts = contracts
        self.events = events
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

        Rolls back when an exception occurs.
        Commits successful transactions.
        Converts unknown database errors into application exceptions.
        """
        if exc_type:
            self.rollback()
            return False

        try:
            self.commit()
        except IntegrityError as exc:
            self.rollback()
            raise DatabaseError() from exc
