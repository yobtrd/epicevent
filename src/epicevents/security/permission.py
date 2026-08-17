from enum import StrEnum


class Permission(StrEnum):
    """Define permissions used for authorization checks."""

    CREATE_USER = "user.create"
    UPDATE_USER = "user.update"
    LIST_USERS = "users.list"
    SHOW_USER = "user.show"
    DEACTIVATE_USER = "user.deactivate"
    CREATE_CLIENT = "create.client"
    UPDATE_CLIENT = "clent.update"
    LIST_CLIENTS = "clients.list"
    SHOW_CLIENT = "client.show"
    CREATE_CONTRACT = "contract.create"
    UPDATE_CONTRACT = "contract.update"
    LIST_CONTRACTS = "contracts.list"
    SHOW_CONTRACT = "contract.show"
    CREATE_EVENT = "event.create"
    UPDATE_EVENT = "event.update"
    LIST_EVENTS = "events.list"
    SHOW_EVENT = "event.show"
    ASSIGN_SUPPORT = "support.assign"
