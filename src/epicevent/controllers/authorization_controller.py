from epicevent.security.permission import Permission
from epicevent.services.authorization_service import AuthorizationService


class AuthorizationController:
    def __init__(self, authorization: AuthorizationService):
        self.authorization = authorization

    def require_permission(self, user, permission: Permission):
        self.authorization.ensure_permission(user, permission)
