from epicevent.exception import RolePermissionError
from epicevent.models.user import User
from epicevent.security import authorization
from epicevent.security.permission import Permission


class AuthorizationService:
    def ensure_permission(self, user: User, permission: Permission):
        if not authorization.has_permission(user, permission):
            raise RolePermissionError()

    def ensure_can_update_user(self, user: User, target_employee_number: str):
        is_management = authorization.has_permission(user, Permission.UPDATE_USER)
        is_owner = user.employee_number == target_employee_number
        if not (is_management or is_owner):
            raise RolePermissionError()
