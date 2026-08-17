from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, TypeAdapter

from epicevents.schemas.types import Email, Name
from epicevents.security.roles import UserRole


def normalize_employee_number(value: str) -> str:
    return value.upper().strip()


EmployeeNumber = Annotated[
    str, Field(min_length=1, max_length=20), AfterValidator(normalize_employee_number)
]


Password = Annotated[str, Field(min_length=8, max_length=120, pattern=r".*[A-Z].*")]

password_validator = TypeAdapter(Password)


class UserCreateBase(BaseModel):
    employee_number: EmployeeNumber
    first_name: Name
    last_name: Name
    email: Email
    password: Password

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class UserCreate(UserCreateBase):
    role_id: UserRole


class SuperuserCreate(UserCreateBase):
    pass


class UserUpdateSelf(BaseModel):
    first_name: Name | None = None
    last_name: Name | None = None
    email: Email | None = None
    password: Password | None = None

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class UserUpdateManagement(BaseModel):
    employee_number: EmployeeNumber | None = None
    first_name: Name | None = None
    last_name: Name | None = None
    email: Email | None = None
    role_id: UserRole | None = None

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class UserResponse(BaseModel):
    id: int
    employee_number: str
    first_name: str
    last_name: str
    email: str
    role_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserDetailResponse(UserResponse):
    is_active: bool
