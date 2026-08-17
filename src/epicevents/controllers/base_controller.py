from typing import TypeVar

from pydantic import BaseModel, ValidationError

from epicevents.exception import InvalidInputError

T = TypeVar("T", bound=BaseModel)


class BaseController:
    @staticmethod
    def _validate(schema: type[T], data: dict) -> T:
        """Validate input data against a Pydantic schema.

        Raises:
            InvalidInputError: If the input data fails schema validation.
        """
        try:
            return schema(**data)
        except ValidationError as e:
            raise InvalidInputError(e.errors()) from e
