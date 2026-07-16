from epicevent.schemas.auth import AuthRequest
from epicevent.schemas.user import UserResponse
from epicevent.services.auth_service import AuthResponse, AuthService


class AuthController:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def login(self, email: str, password: str) -> AuthResponse:
        request = AuthRequest(
            email=email,
            password=password,
        )

        return self.auth_service.authenticate(request)

    def get_current_user(self, token: str) -> UserResponse:
        return self.auth_service.get_current_user(token)
