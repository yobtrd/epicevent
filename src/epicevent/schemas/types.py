from typing import Annotated

from pydantic import AfterValidator, EmailStr, Field


def normalize_email(value: str) -> str:
    return value.lower().strip()


Name = Annotated[str, Field(min_length=1, max_length=50)]


Email = Annotated[EmailStr, Field(max_length=100), AfterValidator(normalize_email)]
