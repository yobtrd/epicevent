from pydantic import ValidationError

from epicevent.exception import InvalidInputError
from epicevent.schemas.user_schema import (
    UserCreate,
    UserResponse,
    UserUpdateManagement,
    UserUpdateSelf,
)
from epicevent.services.user_service import UserService


class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def get_user_by_employee_number(self, employee_number: str) -> UserResponse:
        user = self.user_service.get_user_by_employee_number(employee_number)
        return UserResponse.model_validate(user)

    def create_user(self, current_user: UserResponse, data: dict) -> UserResponse:
        try:
            request = UserCreate(**data)
        except ValidationError as e:
            raise InvalidInputError(e.errors()) from e
        user = self.user_service.create_user(current_user, request)
        return UserResponse.model_validate(user)

    def update_self(self, current_user: UserResponse, data: dict) -> UserResponse:
        try:
            request = UserUpdateSelf(**data)
        except ValidationError as e:
            raise InvalidInputError(e.errors()) from e

        user = self.user_service.update_self(current_user, request)
        return UserResponse.model_validate(user)

    def update_user(
        self, current_user: UserResponse, employee_number: str, data: dict
    ) -> UserResponse:
        try:
            request = UserUpdateManagement(**data)
        except ValidationError as e:
            raise InvalidInputError(e.errors()) from e

        user = self.user_service.update_user(current_user, employee_number, request)
        return UserResponse.model_validate(user)

    def deactivate_user(self, current_user: UserResponse, employee_number: str):
        user = self.user_service.deactivate(current_user, employee_number)
        return UserResponse.model_validate(user)
