from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    employee_number: str
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    role_id: int

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


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )
