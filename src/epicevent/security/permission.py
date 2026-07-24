from enum import StrEnum


class Permission(StrEnum):
    CREATE_USER = "user.create"
    UPDATE_USER = "user.update"
    DEACTIVATE_USER = "user.deactivate"
