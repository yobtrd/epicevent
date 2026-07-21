from epicevent.schemas.auth_schema import AuthRequest
from epicevent.schemas.user_schema import UserResponse
from epicevent.services.auth_service import AuthResponse, AuthService


class AuthController:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def login(self, credentials: dict) -> AuthResponse:
        request = AuthRequest(**credentials)

        return self.auth_service.authenticate(request)

    def get_current_user(self, token: str) -> UserResponse:
        return self.auth_service.get_current_user(token)

    def refresh_session(self, refresh_token: str) -> AuthResponse:
        return self.auth_service.refresh_session(refresh_token)
