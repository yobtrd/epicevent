from enum import StrEnum


class Permission(StrEnum):
    CREATE_USER = "user.create"
    UPDATE_USER = "user.update"
    DEACTIVATE_USER = "user.deactivate"
    CREATE_CLIENT = "create.client"
    UPDATE_CLIENT = "clent.update"
    LIST_CLIENT = "client.list"
    CREATE_CONTRACT = "contract.create"
