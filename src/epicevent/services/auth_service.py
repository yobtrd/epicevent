from epicevent.exception import (
    AuthenticationError,
    ExpiredTokenError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserDisabledError,
    UserNotFoundError,
)
from epicevent.infrastructure.unit_of_work import UnitOfWork
from epicevent.models.user import User
from epicevent.schemas.auth_schema import (
    AuthRequest,
    AuthResponse,
    SessionResult,
    TokenPairs,
    TokenPayload,
)
from epicevent.schemas.user_schema import UserResponse
from epicevent.services.password_service import PasswordService
from epicevent.services.token_service import TokenService


class AuthService:
    """Handle user authentication and session management."""

    def __init__(
        self,
        uow: UnitOfWork,
        token_service: TokenService,
        password_service: PasswordService,
    ) -> None:
        self.uow = uow
        self.token_service = token_service
        self.password_service = password_service

    def _get_user_by_payload(self, payload: TokenPayload) -> User:
        user = self.uow.users.find_by_id(payload.sub)
        if not user:
            raise UserNotFoundError()
        return user

    def authenticate(self, request: AuthRequest) -> AuthResponse:
        """
        Authenticate a user and create a new session.

        Raises:
            InvalidCredentialsError: If the credentials are invalid.
            UserDisabledError: If the user account is disabled.
        """
        with self.uow:
            user = self.uow.users.find_by_email(request.email)
            if not user:
                raise InvalidCredentialsError()

            password_check = self.password_service.verify(
                user.password_hash, request.password
            )
            if not password_check:
                raise InvalidCredentialsError()

            if not user.is_active:
                raise UserDisabledError()

            access_token = self.token_service.create_access_token(user)
            refresh_token = self.token_service.create_refresh_token(user)
            user = UserResponse.model_validate(user)

            return AuthResponse(
                user=user,
                access_token=access_token,
                refresh_token=refresh_token,
            )

    def get_current_user(self, token: str) -> UserResponse:
        """
        Retrieve the authenticated user from an access token.

        Raises:
            ExpiredTokenError: If the token has expired.
            InvalidTokenError: If the token is invalid.
            UserNotFoundError: If the user does not exist.
        """
        payload = self.token_service.decode_token(token, "access")
        with self.uow:
            user = self._get_user_by_payload(payload)
            return UserResponse.model_validate(user)

    def refresh_session(self, refresh_token: str) -> SessionResult:
        """
        Create a new session from a valid refresh token.

        Raises:
            ExpiredTokenError: If the refresh token has expired.
            InvalidTokenError: If the refresh token is invalid.
            UserNotFoundError: If the user does not exist.
        """
        payload = self.token_service.decode_token(refresh_token, "refresh")
        with self.uow:
            user = self._get_user_by_payload(payload)
            access_token = self.token_service.create_access_token(user)
            refresh_token = self.token_service.create_refresh_token(user)

            user = UserResponse.model_validate(user)
            new_tokens = TokenPairs(
                access_token=access_token, refresh_token=refresh_token
            )
            return SessionResult(user=user, new_tokens=new_tokens)

    def authenticate_session(
        self,
        access_token: str | None,
        refresh_token: str | None,
    ) -> SessionResult:
        """
        Authenticate a session using stored tokens.

        A session requires both an access token and a refresh token.
        The access token is used when valid and the session is refreshed
        when the access token has expired.

        Raises:
            AuthenticationError: If the session cannot be restored.
        """
        if not access_token or not refresh_token:
            raise AuthenticationError()
        try:
            try:
                user = self.get_current_user(access_token)
                return SessionResult(user=user)
            except ExpiredTokenError:
                return self.refresh_session(refresh_token)

        except (ExpiredTokenError, InvalidTokenError, UserNotFoundError) as exc:
            raise AuthenticationError() from exc
