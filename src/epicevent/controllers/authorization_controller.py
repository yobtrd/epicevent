from epicevent.schemas.user_schema import UserUpdate
from epicevent.security.permission import Permission
from epicevent.services.authorization_service import AuthorizationService


class AuthorizationController:
    def __init__(self, authorization: AuthorizationService):
        self.authorization = authorization

    def require_permission(self, user: UserUpdate, permission: Permission):
        self.authorization.ensure_permission(user, permission)

    def ensure_can_update_user(self, user: UserUpdate, target_employee_number: str):
        self.authorization.ensure_can_update_user(user, target_employee_number)
