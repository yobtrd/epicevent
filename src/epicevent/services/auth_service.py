from epicevent.exception import InvalidCredentialsError, UserNotFoundError
from epicevent.infrastructure.unit_of_work import UnitOfWork
from epicevent.models.user import User
from epicevent.schemas.auth_schema import AuthRequest, AuthResponse, TokenPayload
from epicevent.schemas.user_schema import UserResponse

from .password_service import PasswordService
from .token_service import TokenService


class AuthService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.password_service = PasswordService()
        self.token_service = TokenService()

    def _get_user_by_payload(self, payload: TokenPayload) -> User:
        user = self.uow.users.find_by_id(payload.sub)
        if not user:
            raise UserNotFoundError()
        return user

    def _issue_tokens(self, user: User) -> AuthResponse:
        access_token = self.token_service.create_access_token(user)
        refresh_token = self.token_service.create_refresh_token(user)
        return AuthResponse(
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def authenticate(self, login: AuthRequest) -> AuthResponse:
        with self.uow:
            user = self.uow.users.find_by_email(login.email)
            if not user:
                raise InvalidCredentialsError()
            password_check = self.password_service.verify(
                user.password_hash, login.password
            )
            if not password_check:
                raise InvalidCredentialsError()

            auth_response = self._issue_tokens(user)
            return auth_response

    def get_current_user(self, token: str) -> UserResponse:
        payload = self.token_service.decode_token(token, "access")
        with self.uow:
            user = self._get_user_by_payload(payload)
            return UserResponse.model_validate(user)

    def refresh_session(self, refresh_token: str) -> AuthResponse:
        payload = self.token_service.decode_token(refresh_token, "refresh")
        with self.uow:
            user = self._get_user_by_payload(payload)
            auth_response = self._issue_tokens(user)
            return auth_response
