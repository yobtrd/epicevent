from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from epicevent.security.roles import UserRole


class UserCreate(BaseModel):
    employee_number: str = Field(min_length=1)
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)
    role_id: UserRole

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    @field_validator("employee_number")
    @classmethod
    def normalize_employee_number(cls, value: str) -> str:
        return value.upper()


class UserResponse(BaseModel):
    id: int
    employee_number: str
    first_name: str
    last_name: str
    email: str
    role_id: int

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )


class UserUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1)
    last_name: str | None = Field(default=None, min_length=1)
    email: EmailStr | None = Field(default=None)
    password: str | None = Field(default=None, min_length=8)

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )
