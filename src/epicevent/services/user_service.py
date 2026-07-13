from src.epicevent.exception import (
    EmailAlreadyExistsError,
    RolePermissionError,
    UserNotFoundError,
)
from src.epicevent.models.user import User
from src.epicevent.schemas.user import UserCreate, UserResponse, UserUpdate
from src.epicevent.security import authorization
from src.epicevent.security.permission import Permission
from src.epicevent.services.password_service import PasswordService
from src.epicevent.unit_of_work import UnitOfWork


class UserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.password_service = PasswordService()

    def _get_user(self, user_id: int) -> User:
        user = self.uow.users.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError
        return user

    def _ensure_management_permission(self, current_user, permission):
        if not authorization.has_permission(current_user, permission):
            raise RolePermissionError

    def create_user(self, current_user, user_dto: UserCreate) -> UserResponse:
        with self.uow:
            self._ensure_management_permission(current_user, Permission.CREATE_USER)
            if self.uow.users.find_by_email(user_dto.email):
                raise EmailAlreadyExistsError()

            hashed_password = self.password_service.hash(user_dto.password)
            data = user_dto.model_dump(exclude={"password"})
            data["password_hash"] = hashed_password

            user = User(**data)
            self.uow.users.create(user)
        return UserResponse.model_validate(user)

    def change_role(self, current_user: User, user_id: int, role_id: int):
        with self.uow:
            self._ensure_management_permission(
                current_user, Permission.UPDATE_USER_ROLE
            )

            user = self._get_user(user_id)

            user.role_id = role_id

    def update_profile(self, current_user, user_id: int, user_data: UserUpdate):
        with self.uow:
            is_management = authorization.has_permission(
                current_user, Permission.UPDATE_USER
            )
            is_owner = authorization.can_update_profile(current_user.id, user_id)
            if not is_management and not is_owner:
                raise RolePermissionError

            user = self._get_user(user_id)

            data = user_data.model_dump(exclude_unset=True)

            for field, value in data.items():
                setattr(user, field, value)

    def deactivate(self, current_user, user_id: int):
        with self.uow:
            self._ensure_management_permission(current_user, Permission.DEACTIVATE_USER)

            user = self._get_user(user_id)

            user.is_active = False
