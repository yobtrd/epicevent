from epicevent.controllers.base_controller import BaseController
from epicevent.schemas.auth_schema import AuthRequest
from epicevent.services.auth_service import AuthResponse, AuthService, SessionResult


class AuthController(BaseController):
    """Coordinate authentication operations."""

    def __init__(self, auth_service: AuthService) -> None:
        self.auth_service = auth_service

    def login(self, data: dict) -> AuthResponse:
        """Authenticate a user with the provided credentials."""
        request = self._validate(AuthRequest, data)
        return self.auth_service.authenticate(request)

    def authenticate_session(
        self,
        access_token: str | None,
        refresh_token: str | None,
    ) -> SessionResult:
        """Authenticate a session using access and refresh tokens."""
        return self.auth_service.authenticate_session(access_token, refresh_token)
