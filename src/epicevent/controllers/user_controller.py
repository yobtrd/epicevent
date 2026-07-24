from pydantic import ValidationError

from epicevent.exception import InvalidInputError, UserNotFoundError
from epicevent.schemas.user_schema import UserCreate, UserResponse, UserUpdate
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

    def update_user(self, current_user: UserResponse, employee_number: str, data: dict):
        try:
            request = UserUpdate(**data)
        except ValidationError as e:
            raise InvalidInputError(e.errors()) from e

        return self.user_service.update_profile(current_user, employee_number, request)

    def verify_user_exists(self, employee_number):
        try:
            self.user_service.get_user_by_employee_number(employee_number)
            return True
        except UserNotFoundError:
            return False

    def update_role(self, current_user, employee_number, role_id):
        return self.user_service.update_role(current_user, employee_number, role_id)
