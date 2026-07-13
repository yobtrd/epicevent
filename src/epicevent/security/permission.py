from enum import StrEnum


class Permission(StrEnum):
    CREATE_USER = "user.create"
    UPDATE_USER = "user.update"
    UPDATE_USER_ROLE = "user.update_role"
    DEACTIVATE_USER = "user.deactivate"
