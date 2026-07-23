class ApplicationError(Exception):
    """Base exception for all application-level errors."""

    pass


# Authentication / Authorization
##################################
class AuthenticationError(ApplicationError):
    """Base exception for authentication-related errors."""

    pass


class InvalidCredentialsError(AuthenticationError):
    pass


class InvalidTokenError(AuthenticationError):
    pass


class ExpiredTokenError(AuthenticationError):
    pass


class InvalidSessionError(AuthenticationError):
    pass


class AuthorizationError(ApplicationError):
    """Base exception for authorization-related errors."""

    pass


class RolePermissionError(AuthorizationError):
    pass


# Domain errors
##################################
class UserNotFoundError(ApplicationError):
    pass


class EmailAlreadyExistsError(ApplicationError):
    pass


class EmployeeNumberAlreadyExistsError(ApplicationError):
    pass


# Validation errors
##################################
class InvalidInputError(ApplicationError):
    def __init__(self, errors: list[dict]):
        super().__init__()
        self.errors = errors


# Persistence errors
##################################
class DatabaseError(ApplicationError):
    """Unexpected database or persistence error."""

    pass
