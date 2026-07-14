from src.epicevent.exception import InvalidCredentialsError, UserNotFoundError
from src.epicevent.schemas.auth import AuthRequest, AuthResponse
from src.epicevent.schemas.user import UserResponse
from src.epicevent.unit_of_work import UnitOfWork

from .password_service import PasswordService
from .token_service import TokenService


class AuthService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.password_service = PasswordService()
        self.token_service = TokenService()

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

            access_token = self.token_service.create_access_token(user)
            refresh_token = self.token_service.create_refresh_token(user)

            return AuthResponse(
                user=user,
                access_token=access_token,
                refresh_token=refresh_token,
            )

    def get_current_user(self, token: str) -> UserResponse:
        with self.uow:
            payload = self.token_service.decode_token(token, "access")

            user = self.uow.users.find_by_id(payload.sub)

            if not user:
                raise UserNotFoundError()

            return UserResponse.model_validate(user)
