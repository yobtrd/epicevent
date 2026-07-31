from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from epicevent.exception import EmailAlreadyExistsError
from epicevent.models import Client


class ClientRepository:
    def __init__(self, session: Session):
        self.session = session

    def _translate_integrity_error(self, exc):
        constraint = exc.orig.diag.constraint_name

        match constraint:
            case "client_email_key":
                raise EmailAlreadyExistsError() from exc

    def save(self, client: Client):
        try:
            self.session.add(client)
            self.session.flush()
            return client
        except IntegrityError as exc:
            self._translate_integrity_error(exc)

    def find_by_email(self, email: str) -> Client | None:
        stmt = select(Client).where(Client.email == email)
        return self.session.scalars(stmt).first()

    def list(self, limit: int = 100, offset: int = 0) -> list[Client]:
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
        return self.session.query(func.count(Client.id)).scalar()
