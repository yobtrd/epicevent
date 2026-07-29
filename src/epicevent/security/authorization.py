from epicevent.exception import RolePermissionError
from epicevent.models.user import User
from epicevent.security.permission import Permission
from epicevent.security.roles import UserRole

ROLE_PERMISSIONS = {
    UserRole.MANAGEMENT: [
        Permission.CREATE_USER,
        Permission.UPDATE_USER,
        Permission.DEACTIVATE_USER,
        Permission.LIST_CLIENT,
    ],
    UserRole.SALES: [
        Permission.CREATE_CLIENT,
        Permission.UPDATE_CLIENT,
        Permission.LIST_CLIENT,
    ],
    UserRole.SUPPORT: [
        Permission.LIST_CLIENT,
    ],
}


def has_permission(user: User, permission: Permission):
    user_permissions = ROLE_PERMISSIONS.get(user.role_id, [])
    return permission in user_permissions


def ensure_permission(user: User, permission: Permission):
    if not has_permission(user, permission):
        raise RolePermissionError()
