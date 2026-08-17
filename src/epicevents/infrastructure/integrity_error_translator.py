from sqlalchemy.exc import IntegrityError

from epicevents.exception import (
    EmailAlreadyExistsError,
    EmployeeNumberAlreadyExistsError,
)


def translate_integrity_error(exc: IntegrityError) -> None:
    """
    Map database integrity errors to domain exceptions.

    Uses PostgreSQL constraint names for precision; falls back to
    re-raising the original IntegrityError for unknown constraints
    or non-PostgreSQL dialects.

    Raises:
        EmailAlreadyExistsError: If email is not unique.
        EmployeeNumberAlreadyExistsError: If employee number is not unique.
        IntegrityError: If the error is unrecognized or dialect is unsupported.
    """
    try:
        constraint = exc.orig.diag.constraint_name
        match constraint:
            case "user_email_key":
                raise EmailAlreadyExistsError() from exc
            case "user_employee_number_key":
                raise EmployeeNumberAlreadyExistsError() from exc
            case "client_email_key":
                raise EmailAlreadyExistsError() from exc
    except AttributeError:
        pass
    raise exc
