from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from epicevent.exception import DatabaseError, EmailAlreadyExistsError
from epicevent.models import Client


class ClientRepository:
    def __init__(self, session: Session):
        self.session = session

    def _translate_integrity_error(self, exc):
        constraint = exc.orig.diag.constraint_name

        match constraint:
            case "client_email_key":
                raise EmailAlreadyExistsError() from exc

            case _:
                raise DatabaseError() from exc

    def save(self, client: Client):
        try:
            self.session.add(client)
            self.session.flush()
            return client
        except IntegrityError as exc:
            self._translate_integrity_error(exc)
