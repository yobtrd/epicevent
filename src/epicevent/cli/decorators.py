from functools import wraps

import epicevent.bootstrap as bootstrap
from epicevent.cli.auth_session import get_authenticated_user
from epicevent.cli.error_handler import (
    display_application_error,
    display_invalid_input_error,
)
from epicevent.exception import ApplicationError, InvalidInputError


def with_app(func):
    """
    Inject an Application instance into a CLI command.

    Creates an application context using the application factory and ensures
    proper cleanup after command execution.

    The decorated function must accept the Application instance as its first
    argument.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        with bootstrap.application_factory.create() as app:
            return func(app, *args, **kwargs)

    return wrapper


def handle_errors(func):
    """
    Handles expected application errors raised by CLI commands.

    Displays validation errors with field-specific messages and translates
    application errors into user-friendly console messages.
    """

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
    """
    Inject the currently authenticated user into a CLI command.

    Retrieves the active user from the CLI authentication session and passes it
    as the second argument after the Application instance.

    The decorated function must accept:
        app: Application
        current_user: UserResponse
    """

    @wraps(func)
    def wrapper(app: bootstrap.Application, *args, **kwargs):
        current_user = get_authenticated_user(app)
        return func(app, current_user, *args, **kwargs)

    return wrapper
