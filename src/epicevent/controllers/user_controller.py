from pydantic import ValidationError

from epicevent.exception import InvalidInputError
from epicevent.schemas.user_schema import UserCreate, UserResponse
from epicevent.services.user_service import UserService


class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def create_user(self, current_user: UserResponse, data: dict) -> UserResponse:
        try:
            request = UserCreate(**data)
            return self.user_service.create_user(current_user, request)
        except ValidationError as e:
            raise InvalidInputError(e.errors()) from e
