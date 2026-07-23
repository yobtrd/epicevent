import click

from epicevent.bootstrap import Application
from epicevent.cli.auth import get_authenticated_user
from epicevent.cli.decorators import with_app
from epicevent.cli.views import user_view
from epicevent.cli.views.error_view import (
    ErrorMessage,
    display_error,
    display_invalid_input_error,
)
from epicevent.exception import (
    EmailAlreadyExistsError,
    EmployeeNumberAlreadyExistsError,
    InvalidInputError,
    UserNotFoundError,
)
from epicevent.security.permission import Permission


@click.group()
def user():
    """user commands."""
    pass


def _handle_user_operation(operation, *args, **kwargs):
    try:
        return operation(*args, **kwargs)
    except EmailAlreadyExistsError:
        display_error(ErrorMessage.EMAIL_ALREADY_EXISTS)
    except EmployeeNumberAlreadyExistsError:
        display_error(ErrorMessage.EMPLOYEE_NUMBER_ALREADY_EXISTS)
    except UserNotFoundError:
        display_error(ErrorMessage.USER_NOT_FOUND)
    except InvalidInputError as e:
        display_invalid_input_error(e)
    return None


@user.command()
@with_app
def create(app: Application):
    auth_user = get_authenticated_user(app)
    app.authorization_controller.require_permission(auth_user, Permission.CREATE_USER)

    data = user_view.ask_user_creation_data()
    operation = app.user_controller.create_user

    user_response = _handle_user_operation(operation, auth_user, data)
    if user_response:
        user_view.display_creation_success(user_response)


@user.command()
@with_app
def update(app: Application):
    auth_user = get_authenticated_user(app)

    employee_number = user_view.ask_target_user_employee_number()
    app.authorization_controller.ensure_can_update_user(auth_user, employee_number)

    operation = app.user_controller.verify_user_exists
    if _handle_user_operation(operation, employee_number) is None:
        return

    data = user_view.ask_user_update_data()
    operation = app.user_controller.update_user

    user_response = _handle_user_operation(
        operation,
        auth_user,
        employee_number,
        data,
    )
    if user_response:
        user_view.display_update_success(user_response)
