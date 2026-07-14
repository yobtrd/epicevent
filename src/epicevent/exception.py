class EmailAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class RolePermissionError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidTokenError(Exception):
    pass
