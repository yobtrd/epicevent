from src.epicevent.exception import InvalidCredentialsError
from src.epicevent.models.user import User
from src.epicevent.unit_of_work import UnitOfWork

from .password_service import PasswordService
from .token_service import TokenService


class AuthService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.password_service = PasswordService()
        self.token_service = TokenService()

    def authenticate(self, email: str, password: str) -> tuple[User, str]:
        user = self.uow.users.find_by_email(email)

        if not user:
            raise (InvalidCredentialsError)
        password_check = self.password_service.verify(user.password_hash, password)
        if not password_check:
            raise (InvalidCredentialsError)

        access_token = self.token_service.create_access_token(user)

        return user, access_token
