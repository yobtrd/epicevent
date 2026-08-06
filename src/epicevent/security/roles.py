from enum import IntEnum


class UserRole(IntEnum):
    """Define application roles used for authorization checks."""

    MANAGEMENT = 1
    SALES = 2
    SUPPORT = 3
