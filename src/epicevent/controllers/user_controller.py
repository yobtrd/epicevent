from pydantic import ValidationError

from epicevent.exception import InvalidInputError, UserNotFoundError
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

    def create_user(self, current_user: UserResponse, data: dict) -> UserResponse:
        try:
            request = UserCreate(**data)
        except ValidationError as e:
            raise InvalidInputError(e.errors()) from e

        return self.user_service.create_user(current_user, request)

    def update_self(self, current_user: UserResponse, data: dict) -> UserResponse:
        try:
            request = UserUpdateSelf(**data)
        except ValidationError as e:
            raise InvalidInputError(e.errors()) from e

        return self.user_service.update_self(current_user, request)

    def update_user(
        self, current_user: UserResponse, employee_number: str, data: dict
    ) -> UserResponse:
        try:
            request = UserUpdateManagement(**data)
        except ValidationError as e:
            raise InvalidInputError(e.errors()) from e

        return self.user_service.update_user(current_user, employee_number, request)

    def verify_user_exists(self, employee_number):
        try:
            self.user_service.get_user_by_employee_number(employee_number)
            return True
        except UserNotFoundError:
            return False
