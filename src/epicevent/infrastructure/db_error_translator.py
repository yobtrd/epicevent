from epicevent.exception import (
    DatabaseError,
    EmailAlreadyExistsError,
    EmployeeNumberAlreadyExistsError,
)


def translate_database_error(exc: Exception) -> Exception:
    constraint = exc.orig.diag.constraint_name

    match constraint:
        case "user_email_key":
            raise EmailAlreadyExistsError()

        case "user_employee_number_key":
            raise EmployeeNumberAlreadyExistsError()

    return DatabaseError()
