from epicevent.exception import RolePermissionError
from epicevent.models.user import User
from epicevent.security.permission import Permission
from epicevent.security.roles import UserRole

ROLE_PERMISSIONS = {
    UserRole.MANAGEMENT: [
        Permission.CREATE_USER,
        Permission.UPDATE_USER,
        Permission.DEACTIVATE_USER,
    ]
}


def has_permission(user: User, permission: Permission):
    user_permissions = ROLE_PERMISSIONS.get(user.role_id, [])
    return permission in user_permissions


def ensure_permission(user: User, permission: Permission):
    if not has_permission(user, permission):
        raise RolePermissionError()
