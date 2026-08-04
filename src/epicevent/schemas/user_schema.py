from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field, TypeAdapter

from epicevent.security.roles import UserRole


def normalize_employee_number(value: str) -> str:
    return value.upper().strip()


EmployeeNumber = Annotated[str, AfterValidator(normalize_employee_number)]


Password = Annotated[str, Field(min_length=8, pattern=r".*[A-Z].*")]

password_validator = TypeAdapter(Password)


class UserCreateBase(BaseModel):
    employee_number: EmployeeNumber = Field(min_length=1)
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: EmailStr
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
    first_name: str | None = Field(default=None, min_length=1)
    last_name: str | None = Field(default=None, min_length=1)
    email: EmailStr | None = Field(default=None)
    password: str | None = Field(default=None, min_length=1)

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class UserUpdateManagement(BaseModel):
    employee_number: EmployeeNumber | None = Field(default=None, min_length=1)
    first_name: str | None = Field(default=None, min_length=1)
    last_name: str | None = Field(default=None, min_length=1)
    email: EmailStr | None = Field(default=None)
    role_id: UserRole | None = Field(default=None)

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
