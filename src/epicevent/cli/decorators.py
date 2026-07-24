from functools import wraps

import epicevent.bootstrap as bootstrap
from epicevent.cli.auth import get_authenticated_user
from epicevent.cli.views.error_view import (
    display_application_error,
    display_invalid_input_error,
)
from epicevent.exception import ApplicationError, InvalidInputError


def with_app(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with bootstrap.application_factory.create() as app:
            return func(app, *args, **kwargs)

    return wrapper


def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except InvalidInputError as error:
            display_invalid_input_error(error)

        except ApplicationError as error:
            display_application_error(error)

        return None

    return wrapper


def require_auth(func):
    @wraps(func)
    def wrapper(app: bootstrap.Application, *args, **kwargs):
        current_user = get_authenticated_user(app)
        return func(app, current_user, *args, **kwargs)

    return wrapper
