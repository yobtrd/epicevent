from enum import IntEnum


class UserRole(IntEnum):
    """
    Define application roles used for authorization checks.

    Role IDs are fixed and synchronized with the database seed migration.
    """

    MANAGEMENT = 1
    SALES = 2
    SUPPORT = 3
