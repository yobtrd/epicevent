from passlib.hash import argon2

from src.epicevent.models.user import User
from src.epicevent.unit_of_work import UnitOfWork


class EmailAlreadyExistsError(Exception):
    pass


class UserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def create(self, user_data: dict) -> User:
        with self.uow:
            if self.uow.user.get_by_email(user_data["email"]):
                raise EmailAlreadyExistsError()

            hashed_password = argon2.hash(user_data["password"])

            user = User(**{**user_data, "password": hashed_password})
            self.uow.user.create(user)
        return user
