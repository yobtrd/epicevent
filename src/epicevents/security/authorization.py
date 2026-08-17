from epicevents.exception import RolePermissionError
from epicevents.models.user import User
from epicevents.security.permission import Permission
from epicevents.security.roles import UserRole

ROLE_PERMISSIONS = {
    UserRole.MANAGEMENT: [
        Permission.CREATE_USER,
        Permission.CREATE_CONTRACT,
        Permission.UPDATE_USER,
        Permission.UPDATE_CONTRACT,
        Permission.UPDATE_EVENT,
        Permission.LIST_USERS,
        Permission.LIST_CLIENTS,
        Permission.LIST_CONTRACTS,
        Permission.LIST_EVENTS,
        Permission.SHOW_USER,
        Permission.SHOW_CLIENT,
        Permission.SHOW_CONTRACT,
        Permission.SHOW_EVENT,
        Permission.DEACTIVATE_USER,
        Permission.ASSIGN_SUPPORT,
    ],
    UserRole.SALES: [
        Permission.CREATE_CLIENT,
        Permission.CREATE_EVENT,
        Permission.UPDATE_CLIENT,
        Permission.UPDATE_CONTRACT,
        Permission.LIST_CLIENTS,
        Permission.LIST_CONTRACTS,
        Permission.LIST_EVENTS,
        Permission.SHOW_CLIENT,
        Permission.SHOW_CONTRACT,
        Permission.SHOW_EVENT,
    ],
    UserRole.SUPPORT: [
        Permission.UPDATE_EVENT,
        Permission.LIST_CLIENTS,
        Permission.LIST_CONTRACTS,
        Permission.LIST_EVENTS,
        Permission.SHOW_CLIENT,
        Permission.SHOW_CONTRACT,
        Permission.SHOW_EVENT,
    ],
}


def has_permission(user: User, permission: Permission) -> bool:
    """Check whether a user has a specific permission."""
    user_permissions = ROLE_PERMISSIONS.get(user.role_id, [])
    return permission in user_permissions


def ensure_permission(user: User, permission: Permission) -> None:
    """
    Ensure that a user has a specific permission.

    Raises:
        RolePermissionError: If the user lacks the required permission.
    """
    if not has_permission(user, permission):
        raise RolePermissionError()
