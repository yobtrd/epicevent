from epicevent.exception import (
    UserNotFoundError,
)
from epicevent.infrastructure.unit_of_work import UnitOfWork
from epicevent.models.user import User
from epicevent.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from epicevent.security.decorators import require_permission
from epicevent.security.permission import Permission
from epicevent.services.authorization_service import AuthorizationService
from epicevent.services.password_service import PasswordService


class UserService:
    def __init__(
        self,
        uow: UnitOfWork,
        password: PasswordService,
        authorization: AuthorizationService,
    ):
        self.uow = uow
        self.password_service = password
        self.authorization = authorization

    def _normalize_employee_number(self, employee_number: str) -> str:
        return employee_number.strip().upper()

    def get_user_by_employee_number(self, employee_number: str) -> User:
        user = self.uow.users.find_by_employee_number(employee_number)
        if user is None:
            raise UserNotFoundError()
        return user

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

    @require_permission(Permission.UPDATE_USER_ROLE)
    def change_role(
        self,
        current_user: UserResponse,
        employee_number: str,
        role_id: int,
    ):
        employee_number = self._normalize_employee_number(employee_number)
        with self.uow:
            user = self.get_user_by_employee_number(employee_number)
            user.role_id = role_id
            return UserResponse.model_validate(user)

    @require_permission(Permission.DEACTIVATE_USER)
    def deactivate(
        self,
        current_user: UserResponse,
        employee_number: str,
    ):
        employee_number = self._normalize_employee_number(employee_number)
        with self.uow:
            user = self.get_user_by_employee_number(employee_number)
            user.is_active = False
            return UserResponse.model_validate(user)

    def update_profile(
        self,
        current_user: UserResponse,
        employee_number: str,
        user_data: UserUpdate,
    ):
        employee_number = self._normalize_employee_number(employee_number)
        with self.uow:
            user = self.get_user_by_employee_number(employee_number)
            self.authorization.ensure_can_update_user(current_user, employee_number)
            data = user_data.model_dump(exclude_unset=True)
            for field, value in data.items():
                if field == "password":
                    value = self.password_service.hash(value)
                setattr(user, field, value)
            self.uow.users.save(user)
            return UserResponse.model_validate(user)
