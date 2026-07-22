from epicevent.security.roles import RoleId

from .permission import Permission

ROLE_PERMISSIONS = {
    RoleId.MANAGEMENT: [
        Permission.CREATE_USER,
        Permission.UPDATE_USER,
        Permission.UPDATE_USER_ROLE,
        Permission.DEACTIVATE_USER,
    ]
}


def has_permission(user, permission):
    user_permissions = ROLE_PERMISSIONS.get(user.role_id, [])
    return permission in user_permissions
