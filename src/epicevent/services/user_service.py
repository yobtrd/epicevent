from src.epicevent.models.user import User
from src.epicevent.schemas.user import UserCreate, UserResponse, UserUpdate
from src.epicevent.services.password_service import PasswordService
from src.epicevent.unit_of_work import UnitOfWork


class EmailAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.password_service = PasswordService()

    def create(self, user_dto: UserCreate) -> UserResponse:
        with self.uow:
            if self.uow.users.get_by_email(user_dto.email):
                raise EmailAlreadyExistsError()

            hashed_password = self.password_service.hash(user_dto.password)
            data = user_dto.model_dump(exclude={"password"})
            data["password_hash"] = hashed_password

            user = User(**data)
            self.uow.users.create(user)
            return UserResponse.model_validate(user)

    def change_role(self, user_id: int, role_id: int):
        with self.uow:
            user = self.uow.users.get_by_id(user_id)
            if user is None:
                raise UserNotFoundError
            user.role_id = role_id

    def update_profile(self, user_id: int, user_data: UserUpdate):
        with self.uow:
            user = self.uow.users.get_by_id(user_id)
            if user is None:
                raise UserNotFoundError

            data = user_data.model_dump(exclude_unset=True)

            for field, value in data.items():
                setattr(user, field, value)

    def deactivate(self, user_id: int):
        with self.uow:
            user = self.uow.users.get_by_id(user_id)
            if user is None:
                raise UserNotFoundError

            user.is_active = False
