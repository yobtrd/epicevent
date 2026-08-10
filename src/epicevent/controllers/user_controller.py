from epicevent.controllers.base_controller import BaseController
from epicevent.schemas.user_schema import (
    SuperuserCreate,
    UserCreate,
    UserDetailResponse,
    UserResponse,
    UserUpdateManagement,
    UserUpdateSelf,
)
from epicevent.services.user_service import UserService


class UserController(BaseController):
    """Coordinate user operations between CLI and services."""

    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    def get_user_by_employee_number(self, employee_number: str) -> UserResponse:
        user = self.user_service.get_user_by_employee_number(employee_number)
        return UserResponse.model_validate(user)

    def ensure_can_create_superuser(self) -> None:
        self.user_service.ensure_can_create_superuser()

    def create_superuser(self, data: dict) -> UserResponse:
        request = self._validate(SuperuserCreate, data)
        superuser = self.user_service.create_superuser(request)
        return UserResponse.model_validate(superuser)

    def create_user(self, current_user: UserResponse, data: dict) -> UserResponse:
        request = self._validate(UserCreate, data)
        user = self.user_service.create_user(current_user, request)
        return UserResponse.model_validate(user)

    def update_self(self, current_user: UserResponse, data: dict) -> UserResponse:
        request = self._validate(UserUpdateSelf, data)
        user = self.user_service.update_self(current_user, request)
        return UserResponse.model_validate(user)

    def update_user(
        self,
        current_user: UserResponse,
        employee_number: str,
        data: dict,
    ) -> UserResponse:
        request = self._validate(UserUpdateManagement, data)
        user = self.user_service.update_user(current_user, employee_number, request)
        return UserResponse.model_validate(user)

    def list_users(
        self,
        current_user: UserResponse,
        include_inactive: bool = False,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[UserResponse], int]:
        users_list, total_count = self.user_service.list_users(
            current_user,
            include_inactive=include_inactive,
            limit=limit,
            offset=offset,
        )
        return (
            [UserResponse.model_validate(user) for user in users_list],
            total_count,
        )

    def show_user(
        self,
        current_user: UserResponse,
        employee_number: str,
    ) -> UserDetailResponse:
        user = self.user_service.show_user(current_user, employee_number)
        return UserDetailResponse.model_validate(user)

    def deactivate_user(
        self,
        current_user: UserResponse,
        employee_number: str,
    ) -> UserResponse:
        user = self.user_service.deactivate(current_user, employee_number)
        return UserResponse.model_validate(user)
