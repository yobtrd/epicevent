from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from epicevent.infrastructure.integrity_error_translator import (
    translate_integrity_error,
)
from epicevent.models import Client


class ClientRepository:
    """Handle data access operations for clients."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, client: Client) -> Client:
        """
        Persist a client instance in the database.

        Uses flush to catch and translate unique constraint violations
        (email) into domain exceptions.
        """
        try:
            self.session.add(client)
            self.session.flush()
            return client
        except IntegrityError as exc:
            translate_integrity_error(exc)

    def find_by_email(self, email: str) -> Client | None:
        stmt = select(Client).where(Client.email == email)
        return self.session.scalars(stmt).first()

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Client]:
        """
        Retrieve a paginated list of clients.

        Eagerly loads the sales_representative to optimize performance.
        """
        return (
            self.session.execute(
                select(Client)
                .options(joinedload(Client.sales_representative))
                .offset(offset)
                .limit(limit)
            )
            .scalars()
            .all()
        )

    def count(self) -> int:
        return self.session.execute(select(func.count(Client.id))).scalar_one()
