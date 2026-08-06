from enum import StrEnum


class Permission(StrEnum):
    """Define permissions used for authorization checks."""

    CREATE_USER = "user.create"
    UPDATE_USER = "user.update"
    LIST_USER = "user.list"
    DEACTIVATE_USER = "user.deactivate"
    CREATE_CLIENT = "create.client"
    UPDATE_CLIENT = "clent.update"
    LIST_CLIENT = "client.list"
    CREATE_CONTRACT = "contract.create"
    UPDATE_CONTRACT = "contract.update"
    LIST_CONTRACT = "contract.list"
    CREATE_EVENT = "event.create"
    UPDATE_EVENT = "event.update"
    LIST_EVENT = "event.list"
    ASSIGN_SUPPORT = "support.assign"
