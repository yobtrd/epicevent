from epicevent.exception import UserAlreadyDeactivatedError, UserNotFoundError
from epicevent.infrastructure.unit_of_work import UnitOfWork
from epicevent.models.user import User
from epicevent.schemas.user_schema import (
    UserCreate,
    UserResponse,
    UserUpdateManagement,
    UserUpdateSelf,
    normalize_employee_number,
)
from epicevent.security.decorators import require_permission
from epicevent.security.permission import Permission
from epicevent.services.password_service import PasswordService


class UserService:
    def __init__(
        self,
        uow: UnitOfWork,
        password_service: PasswordService,
    ):
        self.uow = uow
        self.password_service = password_service

    def get_user_by_employee_number(self, employee_number: str) -> User:
        user = self.uow.users.find_by_employee_number(employee_number)
        if user is None:
            raise UserNotFoundError()
        return user

    def _apply_user_updates(self, user: User, data: dict):
        for field, value in data.items():
            if field == "password":
                user.password_hash = self.password_service.hash(value)
            else:
                setattr(user, field, value)
        self.uow.users.save(user)

    @require_permission(Permission.CREATE_USER)
    def create_user(
        self,
        current_user: UserResponse,
        user_dto: UserCreate,
    ) -> UserResponse:
        with self.uow:
            hashed_password = self.password_service.hash(user_dto.password)
            data = user_dto.model_dump(exclude={"password"})
            data["password_hash"] = hashed_password

            user = User(**data)
            self.uow.users.save(user)
            return UserResponse.model_validate(user)

    def update_self(self, current_user: UserResponse, user_data: UserUpdateSelf):
        with self.uow:
            user = self.get_user_by_employee_number(current_user.employee_number)
            self._apply_user_updates(user, user_data.model_dump(exclude_unset=True))
            return UserResponse.model_validate(user)

    @require_permission(Permission.UPDATE_USER)
    def update_user(
        self,
        current_user: UserResponse,
        employee_number: str,
        user_data: UserUpdateManagement,
    ):
        employee_number = normalize_employee_number(employee_number)
        with self.uow:
            user = self.get_user_by_employee_number(employee_number)
            self._apply_user_updates(user, user_data.model_dump(exclude_unset=True))
            return UserResponse.model_validate(user)

    @require_permission(Permission.DEACTIVATE_USER)
    def deactivate(
        self,
        current_user: UserResponse,
        employee_number: str,
    ):
        employee_number = normalize_employee_number(employee_number)
        with self.uow:
            user = self.get_user_by_employee_number(employee_number)
            if not user.is_active:
                raise UserAlreadyDeactivatedError()
            user.is_active = False
            return UserResponse.model_validate(user)
