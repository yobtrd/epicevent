from epicevent.exception import RolePermissionError
from epicevent.security import authorization
from epicevent.security.permission import Permission


class AuthorizationService:
    def ensure_permission(self, user, permission):
        if not authorization.has_permission(user, permission):
            raise RolePermissionError()

    def ensure_can_create_user(self, user):
        self.ensure_permission(
            user,
            Permission.CREATE_USER,
        )

    def ensure_can_change_role(self, user):
        self.ensure_permission(
            user,
            Permission.UPDATE_USER_ROLE,
        )

    def ensure_can_update_user(self, user, target_user_id):
        is_management = authorization.has_permission(
            user,
            Permission.UPDATE_USER,
        )

        is_owner = authorization.can_update_profile(
            user.id,
            target_user_id,
        )

        if not is_management and not is_owner:
            raise RolePermissionError()

    def ensure_can_deactivate_user(self, user):
        self.ensure_permission(
            user,
            Permission.DEACTIVATE_USER,
        )
