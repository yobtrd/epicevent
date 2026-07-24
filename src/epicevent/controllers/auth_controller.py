from epicevent.schemas.auth_schema import AuthRequest
from epicevent.services.auth_service import AuthResponse, AuthService, SessionResult


class AuthController:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def login(self, credentials: dict) -> AuthResponse:
        request = AuthRequest(**credentials)

        return self.auth_service.authenticate(request)

    def authenticate_session(
        self, access_token: str, refresh_token: str
    ) -> SessionResult:
        return self.auth_service.authenticate_session(access_token, refresh_token)
